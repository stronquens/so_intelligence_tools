from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import httpx


CHANGE_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE = "hwdsl2/whisper-server:latest"
DEFAULT_BASELINE_URL = "http://127.0.0.1:9000"
DEFAULT_RESULTS_DIR = CHANGE_DIR / "evidence"


@dataclass(slots=True)
class ServerSpec:
    model: str
    base_url: str
    container_name: str | None = None
    volume_name: str | None = None
    startup_seconds: float | None = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True, type=Path)
    parser.add_argument("--reference-text", type=Path, default=None)
    parser.add_argument("--models", nargs="+", default=["small", "medium"])
    parser.add_argument("--max-seconds", type=float, default=15.0)
    parser.add_argument("--timeout-seconds", type=float, default=1200.0)
    parser.add_argument("--transcription-timeout-seconds", type=float, default=120.0)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args()

    args.results_dir.mkdir(parents=True, exist_ok=True)
    sample_path = args.sample.resolve()
    reference_text = (
        args.reference_text.read_text(encoding="utf-8").strip()
        if args.reference_text
        else None
    )

    with tempfile.TemporaryDirectory(prefix="so-ai-whisper-bench-") as tmp_dir:
        prepared_sample = prepare_sample(
            sample_path,
            Path(tmp_dir) / "sample.wav",
            max_seconds=args.max_seconds,
        )
        audio_duration = wav_duration_seconds(prepared_sample)

        results: list[dict] = []
        baseline = ServerSpec(model="large-v3-turbo", base_url=DEFAULT_BASELINE_URL)
        print(f"Benchmarking warm baseline {baseline.model} at {baseline.base_url}", flush=True)
        baseline_result = benchmark_server(
            baseline,
            prepared_sample,
            audio_duration=audio_duration,
            transcription_timeout_seconds=args.transcription_timeout_seconds,
            reference_text=reference_text,
            pseudo_reference_text=None,
        )
        results.append(baseline_result)
        pseudo_reference = reference_text or str(baseline_result.get("text") or "")

        for index, model in enumerate(args.models, start=1):
            port = 9100 + index
            spec = ServerSpec(
                model=model,
                base_url=f"http://127.0.0.1:{port}",
                container_name=f"so-ai-whisper-bench-{safe_name(model)}",
                volume_name=f"so-ai-whisper-bench-{safe_name(model)}-data",
            )
            print(
                f"Benchmarking temporary candidate {model} at {spec.base_url}",
                flush=True,
            )
            result = benchmark_temporary_container(
                spec,
                prepared_sample,
                audio_duration=audio_duration,
                image=args.image,
                host_port=port,
                startup_timeout_seconds=args.timeout_seconds,
                transcription_timeout_seconds=args.transcription_timeout_seconds,
                reference_text=reference_text,
                pseudo_reference_text=pseudo_reference,
            )
            results.append(result)

    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sample": str(sample_path),
        "max_seconds": args.max_seconds,
        "reference_mode": "human" if reference_text else "large-v3-turbo pseudo-reference",
        "results": results,
    }
    json_path = args.results_dir / "whisper-cpu-benchmark-results.json"
    md_path = args.results_dir / "whisper-cpu-benchmark-summary.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_summary(payload), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


def benchmark_temporary_container(
    spec: ServerSpec,
    sample_path: Path,
    *,
    audio_duration: float,
    image: str,
    host_port: int,
    startup_timeout_seconds: float,
    transcription_timeout_seconds: float,
    reference_text: str | None,
    pseudo_reference_text: str,
) -> dict:
    assert spec.container_name
    assert spec.volume_name
    started = time.perf_counter()
    try:
        run(["docker", "volume", "create", spec.volume_name])
        run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                spec.container_name,
                "-p",
                f"127.0.0.1:{host_port}:9000",
                "-e",
                f"WHISPER_MODEL={spec.model}",
                "-e",
                "WHISPER_DEVICE=cpu",
                "-e",
                "WHISPER_COMPUTE_TYPE=int8",
                "-e",
                "WHISPER_BEAM=1",
                "-e",
                "HF_HOME=/var/lib/whisper",
                "-e",
                "HUGGINGFACE_HUB_CACHE=/var/lib/whisper",
                "-e",
                "XDG_CACHE_HOME=/var/lib/whisper",
                "-e",
                "TRANSFORMERS_CACHE=/var/lib/whisper",
                "-v",
                f"{spec.volume_name}:/var/lib/whisper",
                image,
            ]
        )
        wait_for_ready(spec.base_url, timeout_seconds=startup_timeout_seconds)
        spec.startup_seconds = time.perf_counter() - started
        return benchmark_server(
            spec,
            sample_path,
            audio_duration=audio_duration,
            transcription_timeout_seconds=transcription_timeout_seconds,
            reference_text=reference_text,
            pseudo_reference_text=pseudo_reference_text,
        )
    except Exception as exc:
        return {
            "model": spec.model,
            "base_url": spec.base_url,
            "status": "failed",
            "startup_seconds": time.perf_counter() - started,
            "error": repr(exc),
        }
    finally:
        run(["docker", "rm", "-f", spec.container_name], check=False)
        run(["docker", "volume", "rm", "-f", spec.volume_name], check=False)


def benchmark_server(
    spec: ServerSpec,
    sample_path: Path,
    *,
    audio_duration: float,
    transcription_timeout_seconds: float,
    reference_text: str | None,
    pseudo_reference_text: str | None,
) -> dict:
    started = time.perf_counter()
    text = transcribe(
        spec.base_url,
        sample_path,
        timeout_seconds=transcription_timeout_seconds,
    )
    elapsed = time.perf_counter() - started
    comparison = reference_text or pseudo_reference_text
    quality = compare_text(text, comparison) if comparison else {}
    return {
        "model": spec.model,
        "base_url": spec.base_url,
        "status": "ok",
        "startup_seconds": spec.startup_seconds,
        "audio_duration_seconds": audio_duration,
        "transcription_seconds": elapsed,
        "realtime_factor": elapsed / audio_duration if audio_duration else None,
        "text": text,
        "quality": quality,
    }


def transcribe(base_url: str, sample_path: Path, *, timeout_seconds: float) -> str:
    with httpx.Client(timeout=timeout_seconds) as client:
        with sample_path.open("rb") as audio_file:
            response = client.post(
                f"{base_url.rstrip('/')}/v1/audio/transcriptions",
                data={
                    "model": "whisper-1",
                    "language": "es",
                    "response_format": "json",
                    "temperature": "0",
                },
                files={"file": ("sample.wav", audio_file, "audio/wav")},
            )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("text") or "").strip()


def wait_for_ready(base_url: str, *, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{base_url.rstrip('/')}/v1/models", timeout=2) as response:
                if 200 <= response.status < 300:
                    return
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"Server did not become ready at {base_url}: {last_error}")


def prepare_sample(source: Path, target: Path, *, max_seconds: float) -> Path:
    if source.suffix.lower() != ".wav":
        raise ValueError(f"Only WAV samples are supported without ffmpeg: {source}")
    with wave.open(str(source), "rb") as src:
        params = src.getparams()
        frames_to_copy = min(src.getnframes(), int(max_seconds * src.getframerate()))
        frames = src.readframes(frames_to_copy)
    with wave.open(str(target), "wb") as dst:
        dst.setparams(params)
        dst.writeframes(frames)
    return target


def wav_duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def compare_text(candidate: str, reference: str | None) -> dict:
    if not reference:
        return {}
    candidate_words = normalize_words(candidate)
    reference_words = normalize_words(reference)
    distance = levenshtein(reference_words, candidate_words)
    return {
        "reference_word_count": len(reference_words),
        "candidate_word_count": len(candidate_words),
        "word_distance": distance,
        "word_error_rate": distance / len(reference_words) if reference_words else None,
    }


def normalize_words(text: str) -> list[str]:
    return re.findall(r"[\wáéíóúüñ]+", text.lower(), flags=re.IGNORECASE)


def levenshtein(a: list[str], b: list[str]) -> int:
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, start=1):
        current = [i]
        for j, right in enumerate(b, start=1):
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + (left != right),
                )
            )
        previous = current
    return previous[-1]


def render_summary(payload: dict) -> str:
    lines = [
        "# Whisper CPU Model Benchmark",
        "",
        f"Sample: `{payload['sample']}`",
        f"Reference mode: {payload['reference_mode']}",
        "",
        "| Model | Status | Startup s | Transcription s | Audio s | RTF | WER/distance |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in payload["results"]:
        quality = result.get("quality") or {}
        wer = quality.get("word_error_rate")
        distance = quality.get("word_distance")
        lines.append(
            "| {model} | {status} | {startup} | {transcription} | {audio} | {rtf} | {quality} |".format(
                model=result.get("model"),
                status=result.get("status"),
                startup=format_float(result.get("startup_seconds")),
                transcription=format_float(result.get("transcription_seconds")),
                audio=format_float(result.get("audio_duration_seconds")),
                rtf=format_float(result.get("realtime_factor")),
                quality=(
                    f"{wer:.3f} / {distance}" if isinstance(wer, float) else ""
                ),
            )
        )
    lines.extend(["", "## Transcripts", ""])
    for result in payload["results"]:
        lines.extend(
            [
                f"### {result.get('model')} ({result.get('status')})",
                "",
                result.get("text") or result.get("error") or "",
                "",
            ]
        )
    return "\n".join(lines)


def format_float(value) -> str:
    return f"{value:.2f}" if isinstance(value, (int, float)) else ""


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-").lower()


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=check)


if __name__ == "__main__":
    raise SystemExit(main())
