## Context

The current machine is CPU-only for local AI audio work. The Whisper ASR benchmark showed that model choice matters: smaller models can reduce latency but quality can drop quickly in Spanish. TTS has the same risk, plus model families differ sharply in API shape: some are simple ONNX/CLI engines, while others are PyTorch/GPU-oriented voice-cloning systems.

## Goals / Non-Goals

**Goals:**

- Identify which candidate TTS models are realistic on CPU before adding a product default.
- Preserve source-backed notes for Spanish support, control features, runtime requirements, and expected feasibility.
- Design the benchmark so downloaded models live in temporary Docker volumes/caches and can be removed after the spike.
- Produce comparable metrics: startup/download time, synthesis time, audio duration, realtime factor, output file path, and subjective quality notes.

**Non-Goals:**

- Add the final OS-level TTS product integration in this change.
- Keep benchmark model weights unless the user explicitly selects a winner.
- Claim production quality from synthetic or single-sentence tests.
- Force GPU-first models into production on CPU if their official runtime is not CPU-suitable.

## Decisions

- Treat Piper, Kokoro ONNX, and NeuTTS Nano Spanish as first-pass CPU candidates because they are small or explicitly CPU/on-device oriented.
- Treat Qwen3-TTS and Chatterbox as higher-quality/control candidates that need feasibility gates before full CPU benchmarking.
- Prefer Dockerized one-shot benchmark runs with bind-mounted input/output and temporary model cache volumes.
- Keep a common Spanish prompt set so output can be compared by latency and listening quality.
- Record primary-source findings in `research/tts-model-candidates.md`.

## Risks / Trade-offs

- Some projects may not publish stable Docker images. Mitigation: use small per-candidate Dockerfiles or one-shot scripts inside the change during the implementation step.
- Qwen3-TTS official examples are CUDA/FlashAttention-oriented. Mitigation: benchmark official CPU only if feasible; otherwise record it as GPU-first and optionally test community CPU/GGUF runtimes separately.
- Voice-cloning models need reference audio and transcript. Mitigation: split benchmark prompts into "no reference" and "reference voice" classes.
- Audio quality is subjective. Mitigation: record output WAVs and notes, and later add human reference prompts if a candidate looks promising.
