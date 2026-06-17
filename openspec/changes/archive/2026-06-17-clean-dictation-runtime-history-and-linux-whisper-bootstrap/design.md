## Context

The code and current docs already use faster-whisper HTTP, but repository history still contained archived experimental runtime artifacts. The Linux desktop installer also enabled the dictation listener without first ensuring the Whisper server was available.

## Goals / Non-Goals

**Goals:**

- Keep repository search free of retired dictation runtime names.
- Start the faster-whisper Docker server during Linux desktop setup.
- Preserve the existing Windows shortcut and Whisper HTTP behavior.

**Non-Goals:**

- Implement a CPU-specific Whisper compose variant.
- Change the dictation listener key bindings.
- Remove unrelated OpenSpec archives.

## Decisions

- Add `ensure-whisper-docker-server` as an explicit CLI command and call the same installer from Linux dictation setup.
- Copy `docker/whisper-server/.env.example` to `.env` only when `.env` is missing, so local GPU/CPU tuning is preserved.
- Remove only archived directories that referenced the retired dictation runtime.

## Risks / Trade-offs

- Docker or GPU setup can fail on a new Linux machine -> the installer now fails with a clear Docker Compose error instead of silently installing a dictation listener without its ASR backend.
- The bundled compose currently targets CUDA -> CPU-only Linux machines will need a compose/env adjustment documented in `docs/whisper-docker.md`.
