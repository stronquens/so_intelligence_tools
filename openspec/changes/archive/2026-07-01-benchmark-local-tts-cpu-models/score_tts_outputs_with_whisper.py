from __future__ import annotations

import json
import re
import time
from pathlib import Path

import httpx


CHANGE_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = CHANGE_DIR / "evidence"
RESULTS_PATH = EVIDENCE_DIR / "tts-cpu-benchmark-results.json"
QUALITY_JSON_PATH = EVIDENCE_DIR / "tts-asr-quality-results.json"
QUALITY_MD_PATH = EVIDENCE_DIR / "tts-asr-quality-summary.md"
WHISPER_URL = "http://127.0.0.1:9000/v1/audio/transcriptions"


def main() -> int:
    payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    rows = []
    for result in payload["results"]:
        if result["status"] != "ok" or not result.get("output_path"):
            continue
        audio_path = CHANGE_DIR / result["output_path"]
        started = time.perf_counter()
        text = transcribe(audio_path)
        elapsed = time.perf_counter() - started
        quality = compare_text(text, result["prompt"])
        rows.append(
            {
                "candidate": result["candidate"],
                "voice": result["voice"],
                "prompt_id": result["prompt_id"],
                "audio_path": result["output_path"],
                "prompt": result["prompt"],
                "transcript": text,
                "asr_seconds": elapsed,
                **quality,
            }
        )
    quality_payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "whisper_url": WHISPER_URL,
        "quality_note": (
            "ASR WER is a proxy for intelligibility only. It does not measure naturalness, "
            "speaker preference, emotion, or prosody."
        ),
        "results": rows,
    }
    QUALITY_JSON_PATH.write_text(
        json.dumps(quality_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    QUALITY_MD_PATH.write_text(render_summary(quality_payload), encoding="utf-8")
    print(f"Wrote {QUALITY_JSON_PATH}")
    print(f"Wrote {QUALITY_MD_PATH}")
    return 0


def transcribe(path: Path) -> str:
    with httpx.Client(timeout=180) as client:
        with path.open("rb") as audio_file:
            response = client.post(
                WHISPER_URL,
                data={
                    "model": "whisper-1",
                    "language": "es",
                    "response_format": "json",
                    "temperature": "0",
                },
                files={"file": (path.name, audio_file, "audio/wav")},
            )
    response.raise_for_status()
    return str(response.json().get("text") or "").strip()


def compare_text(candidate: str, reference: str) -> dict:
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
        "# TTS ASR Quality Proxy",
        "",
        payload["quality_note"],
        "",
        "| Candidate | Voice | Prompt | WER | Distance | ASR s | Audio |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["results"]:
        wer = row["word_error_rate"]
        lines.append(
            "| {candidate} | {voice} | {prompt_id} | {wer} | {distance} | {asr} | {audio} |".format(
                candidate=row["candidate"],
                voice=row["voice"],
                prompt_id=row["prompt_id"],
                wer=f"{wer:.3f}" if isinstance(wer, float) else "",
                distance=row["word_distance"],
                asr=f"{row['asr_seconds']:.2f}",
                audio=row["audio_path"],
            )
        )
    lines.extend(["", "## Transcripts", ""])
    for row in payload["results"]:
        lines.extend(
            [
                f"### {row['candidate']} / {row['voice']} / {row['prompt_id']}",
                "",
                f"Prompt: {row['prompt']}",
                "",
                f"Whisper transcript: {row['transcript']}",
                "",
            ]
        )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
