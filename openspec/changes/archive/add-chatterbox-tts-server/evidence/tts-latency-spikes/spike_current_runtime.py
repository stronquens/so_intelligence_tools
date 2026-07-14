from __future__ import annotations

import json
import sys
import time
import traceback
import wave
from pathlib import Path

import torch

sys.path.insert(0, "/app")

from server import ChatterboxRuntime, tensor_to_wav_bytes


OUT_DIR = Path("/evidence")
TEXT = (
    "He terminado la comprobacion del monitor de Codex Desktop. "
    "La voz femenina esta funcionando, pero vamos a medir si podemos reducir "
    "la latencia sin perder naturalidad ni claridad."
)


def wav_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes() / float(handle.getframerate())


def optimize(runtime: ChatterboxRuntime, mode: str) -> str:
    model = runtime._model
    if model is None:
        return "model-not-loaded"
    if mode == "bf16_t3":
        model.t3.to(dtype=torch.bfloat16)
        model.conds.t3.to(dtype=torch.bfloat16)
        return "t3+conds.t3 bf16"
    return "none"


def synth(runtime: ChatterboxRuntime, label: str, cfg_weight: float) -> dict:
    assert runtime._model is not None
    started = time.perf_counter()
    wav = runtime._model.generate(
        TEXT,
        language_id="es",
        audio_prompt_path=runtime._voices["female"].audio_prompt_path,
        exaggeration=runtime._voices["female"].exaggeration,
        cfg_weight=cfg_weight,
        temperature=runtime._voices["female"].temperature,
    )
    elapsed = time.perf_counter() - started
    wav_path = OUT_DIR / f"{label}.wav"
    wav_path.write_bytes(tensor_to_wav_bytes(wav, runtime._model.sr))
    audio_seconds = wav_seconds(wav_path)
    return {
        "label": label,
        "cfg_weight": cfg_weight,
        "elapsed_seconds": elapsed,
        "audio_seconds": audio_seconds,
        "rtf": elapsed / audio_seconds if audio_seconds else None,
        "wav_path": str(wav_path),
        "text_chars": len(TEXT),
    }


def main() -> int:
    summary: dict = {
        "backend": "current_chatterbox_pytorch_direct",
        "torch": torch.__version__,
        "cuda": torch.cuda.is_available(),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "results": [],
    }
    try:
        runtime = ChatterboxRuntime()
        load_started = time.perf_counter()
        runtime.load()
        summary["load_seconds"] = time.perf_counter() - load_started
        summary["load_notes"] = runtime._load_notes
        for mode in ["none", "bf16_t3"]:
            summary[f"optimize_{mode}"] = optimize(runtime, mode)
            for cfg in [0.35, 0.25, 0.15]:
                # Warm up once for the mode/cfg, then record the following run.
                synth(runtime, f"current_direct_{mode}_warmup_cfg_{cfg}", cfg)
                summary["results"].append(
                    synth(runtime, f"current_direct_{mode}_cfg_{cfg}", cfg)
                )
    except Exception as exc:
        summary["error"] = repr(exc)
        summary["traceback"] = traceback.format_exc()
    (OUT_DIR / "current-pytorch-direct-bf16-spike.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0 if "error" not in summary else 1


if __name__ == "__main__":
    raise SystemExit(main())
