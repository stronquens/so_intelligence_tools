from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import time
import venv
import wave
from dataclasses import dataclass
from pathlib import Path


CHANGE_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = CHANGE_DIR / "evidence"
AUDIO_DIR = EVIDENCE_DIR / "audio"


PROMPTS = {
    "neutral": "Hola, estoy probando una voz local en espanol para integrarla con mis herramientas del sistema operativo.",
    "clear": "Cuando suelte el atajo, quiero que el sistema responda con una voz clara, natural y rapida. La pronunciacion en espanol de Espana me importa bastante.",
    "expressive": "Vale, esto ya empieza a sonar mejor. Dilo con un tono tranquilo, cercano y un poco entusiasmado, como si explicaras algo util a un companero.",
}


@dataclass(slots=True)
class RunResult:
    candidate: str
    model: str
    voice: str
    prompt_id: str
    prompt: str
    status: str
    setup_seconds: float | None = None
    synthesis_seconds: float | None = None
    audio_duration_seconds: float | None = None
    realtime_factor: float | None = None
    output_path: str | None = None
    command: str | None = None
    notes: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "candidate": self.candidate,
            "model": self.model,
            "voice": self.voice,
            "prompt_id": self.prompt_id,
            "prompt": self.prompt,
            "status": self.status,
            "setup_seconds": self.setup_seconds,
            "synthesis_seconds": self.synthesis_seconds,
            "audio_duration_seconds": self.audio_duration_seconds,
            "realtime_factor": self.realtime_factor,
            "output_path": self.output_path,
            "command": self.command,
            "notes": self.notes,
            "error": self.error,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        nargs="+",
        default=["piper", "kokoro", "neutts-probe", "chatterbox-probe", "qwen-probe"],
    )
    parser.add_argument("--probe-timeout-seconds", type=float, default=180.0)
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    results: list[RunResult] = []
    temp_root = Path(tempfile.mkdtemp(prefix="so-ai-tts-bench-"))
    try:
        if "piper" in args.candidates:
            results.extend(run_piper(temp_root / "piper"))
        if "kokoro" in args.candidates:
            results.extend(run_kokoro(temp_root / "kokoro"))
        if "neutts-probe" in args.candidates:
            results.extend(run_model_metadata_probe("neutts-nano-spanish", "neuphonic/neutts-nano-spanish", notes=(
                "Metadata probe only. Manual GitHub runtime install did not complete within the practical first-pass window; "
                "needs a dedicated runner before synthesis can be compared."
            )))
        if "chatterbox-probe" in args.candidates:
            results.extend(run_model_metadata_probe("chatterbox", "ResembleAI/chatterbox", notes=(
                "Metadata probe only. pip install probe reached the practical first-pass limit before synthesis; "
                "full 0.5B synthesis should be run as a separate isolated test."
            )))
        if "qwen-probe" in args.candidates:
            results.extend(run_qwen_probe(timeout_seconds=args.probe_timeout_seconds))
    finally:
        if args.keep_temp:
            print(f"Kept temp root: {temp_root}")
        else:
            shutil.rmtree(temp_root, ignore_errors=True)

    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "prompts": PROMPTS,
        "results": [result.to_dict() for result in results],
    }
    json_path = EVIDENCE_DIR / "tts-cpu-benchmark-results.json"
    summary_path = EVIDENCE_DIR / "tts-cpu-benchmark-summary.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary_path.write_text(render_summary(payload), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {summary_path}")
    return 0


def run_piper(work_dir: Path) -> list[RunResult]:
    from huggingface_hub import hf_hub_download

    started = time.perf_counter()
    work_dir.mkdir(parents=True, exist_ok=True)
    venv_dir = work_dir / "venv"
    create_venv(venv_dir)
    pip_install(venv_dir, ["piper-tts"])
    setup_seconds = time.perf_counter() - started

    voices = [
        (
            "es_ES-davefx-medium",
            "es/es_ES/davefx/medium/es_ES-davefx-medium.onnx",
            "es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json",
        ),
        (
            "es_ES-sharvard-medium",
            "es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx",
            "es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json",
        ),
    ]

    results: list[RunResult] = []
    for voice_name, model_file, config_file in voices:
        model_path = Path(
            hf_hub_download(
                "rhasspy/piper-voices",
                filename=model_file,
                local_dir=work_dir / "models",
                local_dir_use_symlinks=False,
            )
        )
        config_path = Path(
            hf_hub_download(
                "rhasspy/piper-voices",
                filename=config_file,
                local_dir=work_dir / "models",
                local_dir_use_symlinks=False,
            )
        )
        for prompt_id, prompt in PROMPTS.items():
            output_path = AUDIO_DIR / f"piper__{voice_name}__{prompt_id}.wav"
            input_path = work_dir / f"{voice_name}-{prompt_id}.txt"
            input_path.write_text(prompt + "\n", encoding="utf-8")
            command = [
                str(python_bin(venv_dir)),
                "-m",
                "piper",
                "-m",
                str(model_path),
                "-c",
                str(config_path),
                "-i",
                str(input_path),
                "-f",
                str(output_path),
            ]
            result = timed_run(command, timeout_seconds=120)
            results.append(
                result_from_completed(
                    candidate="piper",
                    model="rhasspy/piper-voices",
                    voice=voice_name,
                    prompt_id=prompt_id,
                    prompt=prompt,
                    setup_seconds=setup_seconds,
                    command=command,
                    completed=result,
                    output_path=output_path,
                    notes="Piper has no explicit emotion control; emotion is only represented by prompt wording.",
                )
            )
    return results


def run_kokoro(work_dir: Path) -> list[RunResult]:
    from huggingface_hub import hf_hub_download

    started = time.perf_counter()
    work_dir.mkdir(parents=True, exist_ok=True)
    venv_dir = work_dir / "venv"
    create_venv(venv_dir)
    pip_install(venv_dir, ["kokoro-onnx", "torch"])
    patch_kokoro_speed_dtype(venv_dir)

    model_path = Path(
        hf_hub_download(
            "onnx-community/Kokoro-82M-v1.0-ONNX",
            filename="onnx/model.onnx",
            local_dir=work_dir / "models",
            local_dir_use_symlinks=False,
        )
    )
    setup_seconds = time.perf_counter() - started
    voices = ["ef_dora", "em_alex"]
    results: list[RunResult] = []
    for voice in voices:
        voice_pt_path = Path(
            hf_hub_download(
                "hexgrad/Kokoro-82M",
                filename=f"voices/{voice}.pt",
                local_dir=work_dir / "models",
                local_dir_use_symlinks=False,
            )
        )
        voice_path = work_dir / "models" / "voices" / f"{voice}.npz"
        convert_torch_voice_to_npz(venv_dir, voice_pt_path, voice_path, voice)
        for prompt_id, prompt in PROMPTS.items():
            output_path = AUDIO_DIR / f"kokoro_onnx__{voice}__{prompt_id}.wav"
            runner_path = work_dir / f"kokoro_runner_{voice}_{prompt_id}.py"
            runner_path.write_text(
                textwrap.dedent(
                    f"""
                    import wave
                    import numpy as np
                    from kokoro_onnx import Kokoro

                    model = Kokoro({str(model_path)!r}, {str(voice_path)!r})
                    audio, sample_rate = model.create({prompt!r}, voice={voice!r}, speed=1.0, lang="es")
                    audio = np.asarray(audio, dtype=np.float32)
                    audio = np.clip(audio, -1.0, 1.0)
                    pcm = (audio * 32767).astype(np.int16)
                    with wave.open({str(output_path)!r}, "wb") as wav:
                        wav.setnchannels(1)
                        wav.setsampwidth(2)
                        wav.setframerate(int(sample_rate))
                        wav.writeframes(pcm.tobytes())
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            command = [str(python_bin(venv_dir)), str(runner_path)]
            result = timed_run(command, timeout_seconds=180)
            results.append(
                result_from_completed(
                    candidate="kokoro-onnx",
                    model="onnx-community/Kokoro-82M-v1.0-ONNX:model.onnx",
                    voice=voice,
                    prompt_id=prompt_id,
                    prompt=prompt,
                    setup_seconds=setup_seconds,
                    command=command,
                    completed=result,
                    output_path=output_path,
                    notes="Kokoro uses prompt wording plus selected voice; no explicit emotion API in this runner.",
                )
            )
    return results


def convert_torch_voice_to_npz(
    venv_dir: Path, source: Path, target: Path, voice_name: str
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    script = target.parent / f"convert_{target.stem}.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import numpy as np
            import torch
            value = torch.load({str(source)!r}, map_location="cpu")
            if hasattr(value, "detach"):
                value = value.detach().cpu().numpy()
            elif isinstance(value, dict):
                value = {{k: (v.detach().cpu().numpy() if hasattr(v, "detach") else v) for k, v in value.items()}}
            np.savez({str(target)!r}, **{{{voice_name!r}: value}})
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    subprocess.run([str(python_bin(venv_dir)), str(script)], check=True, text=True)


def patch_kokoro_speed_dtype(venv_dir: Path) -> None:
    script = venv_dir / "patch_kokoro_speed_dtype.py"
    script.write_text(
        textwrap.dedent(
            """
            from pathlib import Path
            import kokoro_onnx
            path = Path(kokoro_onnx.__file__)
            text = path.read_text(encoding="utf-8")
            old = '"speed": np.array([speed], dtype=np.int32),'
            new = '"speed": np.array([speed], dtype=np.float32),'
            if old in text:
                path.write_text(text.replace(old, new), encoding="utf-8")
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    subprocess.run([str(python_bin(venv_dir)), str(script)], check=True, text=True)


def run_install_probe(
    *,
    name: str,
    model: str,
    install_command: list[str],
    timeout_seconds: float,
    notes: str,
) -> list[RunResult]:
    work_dir = Path(tempfile.mkdtemp(prefix=f"so-ai-tts-{safe_name(name)}-"))
    started = time.perf_counter()
    env = os.environ.copy()
    env.update(cache_env(work_dir / "cache"))
    try:
        venv_dir = work_dir / "venv"
        create_venv(venv_dir)
        command = [str(python_bin(venv_dir)), "-m", *install_command]
        completed = timed_run(command, timeout_seconds=timeout_seconds, env=env)
        setup_seconds = time.perf_counter() - started
        status = "ok" if completed.returncode == 0 else "failed"
        error = None if status == "ok" else trim_text(completed.stderr or completed.stdout)
        return [
            RunResult(
                candidate=name,
                model=model,
                voice="probe",
                prompt_id="install_probe",
                prompt="",
                status=status,
                setup_seconds=setup_seconds,
                command=" ".join(command),
                notes=notes,
                error=error,
            )
        ]
    except subprocess.TimeoutExpired as exc:
        return [
            RunResult(
                candidate=name,
                model=model,
                voice="probe",
                prompt_id="install_probe",
                prompt="",
                status="not_cpu_feasible",
                setup_seconds=time.perf_counter() - started,
                command=" ".join([str(python_bin(work_dir / "venv")), "-m", *install_command]),
                notes=notes,
                error=f"Install probe exceeded {timeout_seconds:.0f}s: {exc}",
            )
        ]
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def run_model_metadata_probe(name: str, repo: str, *, notes: str) -> list[RunResult]:
    from huggingface_hub import model_info

    started = time.perf_counter()
    try:
        info = model_info(repo, files_metadata=True)
        size = sum(s.size or 0 for s in info.siblings)
        return [
            RunResult(
                candidate=name,
                model=repo,
                voice="metadata",
                prompt_id="metadata_probe",
                prompt="",
                status="not_run",
                setup_seconds=time.perf_counter() - started,
                command=f"huggingface_hub.model_info({repo!r})",
                notes=f"{notes} Repository file size is approximately {size / (1024 ** 3):.2f} GiB.",
            )
        ]
    except Exception as exc:
        return [
            RunResult(
                candidate=name,
                model=repo,
                voice="metadata",
                prompt_id="metadata_probe",
                prompt="",
                status="failed",
                setup_seconds=time.perf_counter() - started,
                command=f"huggingface_hub.model_info({repo!r})",
                error=repr(exc),
                notes=notes,
            )
        ]


def run_qwen_probe(*, timeout_seconds: float) -> list[RunResult]:
    from huggingface_hub import model_info

    started = time.perf_counter()
    repos = [
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    ]
    results: list[RunResult] = []
    for repo in repos:
        try:
            info = model_info(repo, files_metadata=True)
            size = sum(s.size or 0 for s in info.siblings)
            results.append(
                RunResult(
                    candidate="qwen3-tts",
                    model=repo,
                    voice="probe",
                    prompt_id="metadata_probe",
                    prompt="",
                    status="not_run",
                    setup_seconds=time.perf_counter() - started,
                    command=f"huggingface_hub.model_info({repo!r})",
                    notes=(
                        "Official examples are CUDA/bfloat16/FlashAttention oriented. "
                        f"Repository file size is approximately {size / (1024 ** 3):.2f} GiB; "
                        "CPU synthesis was not attempted in this first pass to avoid large retained downloads."
                    ),
                )
            )
        except Exception as exc:
            results.append(
                RunResult(
                    candidate="qwen3-tts",
                    model=repo,
                    voice="probe",
                    prompt_id="metadata_probe",
                    prompt="",
                    status="failed",
                    setup_seconds=time.perf_counter() - started,
                    error=repr(exc),
                    notes=f"Metadata probe failed before the {timeout_seconds:.0f}s feasibility window.",
                )
            )
    return results


def create_venv(path: Path) -> None:
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(path)
    pip_install(path, ["--upgrade", "pip"])


def pip_install(venv_dir: Path, packages: list[str]) -> None:
    command = [str(python_bin(venv_dir)), "-m", "pip", "install", "-q", *packages]
    subprocess.run(command, check=True, text=True)


def python_bin(venv_dir: Path) -> Path:
    return venv_dir / "bin" / "python"


def timed_run(
    command: list[str],
    *,
    timeout_seconds: float,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        env=env,
    )
    completed.elapsed_seconds = time.perf_counter() - started  # type: ignore[attr-defined]
    return completed


def result_from_completed(
    *,
    candidate: str,
    model: str,
    voice: str,
    prompt_id: str,
    prompt: str,
    setup_seconds: float,
    command: list[str],
    completed: subprocess.CompletedProcess[str],
    output_path: Path,
    notes: str,
) -> RunResult:
    synthesis_seconds = float(getattr(completed, "elapsed_seconds"))
    if completed.returncode != 0:
        return RunResult(
            candidate=candidate,
            model=model,
            voice=voice,
            prompt_id=prompt_id,
            prompt=prompt,
            status="failed",
            setup_seconds=setup_seconds,
            synthesis_seconds=synthesis_seconds,
            output_path=str(output_path),
            command=" ".join(command),
            notes=notes,
            error=trim_text(completed.stderr or completed.stdout),
        )
    duration = wav_duration_seconds(output_path) if output_path.exists() else None
    return RunResult(
        candidate=candidate,
        model=model,
        voice=voice,
        prompt_id=prompt_id,
        prompt=prompt,
        status="ok",
        setup_seconds=setup_seconds,
        synthesis_seconds=synthesis_seconds,
        audio_duration_seconds=duration,
        realtime_factor=(synthesis_seconds / duration) if duration else None,
        output_path=str(output_path.relative_to(CHANGE_DIR)),
        command=" ".join(command),
        notes=notes,
    )


def wav_duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def cache_env(cache_dir: Path) -> dict[str, str]:
    return {
        "HF_HOME": str(cache_dir / "hf"),
        "HUGGINGFACE_HUB_CACHE": str(cache_dir / "hf"),
        "TRANSFORMERS_CACHE": str(cache_dir / "hf"),
        "XDG_CACHE_HOME": str(cache_dir / "xdg"),
        "PIP_CACHE_DIR": str(cache_dir / "pip"),
    }


def render_summary(payload: dict) -> str:
    lines = [
        "# Local TTS CPU Benchmark",
        "",
        "## Results",
        "",
        "| Candidate | Voice | Prompt | Status | Setup s | Synth s | Audio s | RTF | Output | Notes |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for result in payload["results"]:
        lines.append(
            "| {candidate} | {voice} | {prompt_id} | {status} | {setup} | {synth} | {audio} | {rtf} | {output} | {notes} |".format(
                candidate=result["candidate"],
                voice=result["voice"],
                prompt_id=result["prompt_id"],
                status=result["status"],
                setup=format_float(result["setup_seconds"]),
                synth=format_float(result["synthesis_seconds"]),
                audio=format_float(result["audio_duration_seconds"]),
                rtf=format_float(result["realtime_factor"]),
                output=result["output_path"] or "",
                notes=(result["notes"] or result["error"] or "").replace("|", "/"),
            )
        )
    lines.extend(["", "## Prompts", ""])
    for key, value in payload["prompts"].items():
        lines.extend([f"### {key}", "", value, ""])
    lines.extend(["", "## Reproduce", ""])
    lines.append(
        "Run `poetry run python openspec/changes/benchmark-local-tts-cpu-models/benchmark_tts_cpu_models.py --candidates piper kokoro neutts-probe chatterbox-probe qwen-probe --probe-timeout-seconds 180`."
    )
    return "\n".join(lines)


def format_float(value) -> str:
    return f"{value:.2f}" if isinstance(value, (int, float)) else ""


def trim_text(value: str, max_chars: int = 1200) -> str:
    value = value.strip()
    return value if len(value) <= max_chars else value[-max_chars:]


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value).strip("-").lower()


if __name__ == "__main__":
    raise SystemExit(main())
