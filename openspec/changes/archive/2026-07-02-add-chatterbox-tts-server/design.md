## Context

The project already has a local TTS client used by Codex voice hooks. Recent workstation benchmarks showed earlier CPU-oriented TTS options were fast but not acceptable to the user, while Chatterbox es-ES produced more promising voices on the RTX 3070. The user selected the female clone sample `cv_female_es_ref_01 / warm` and wants a pausable service that can be integrated from Codex and OpenClaw.

## Goals / Non-Goals

**Goals:**

- Add a Docker Compose service for Chatterbox es-ES that can be started and stopped independently to release GPU VRAM.
- Serve a stable local HTTP API with per-request `voice` selection.
- Include at least `male` and `female` voice presets.
- Expose health and metrics endpoints for readiness and operational observation.
- Reuse the existing `LocalTtsClient` and Codex voice hooks by keeping `/v1/audio/speech` compatible.
- Add CLI lifecycle commands that mirror the warm local service pattern.

**Non-Goals:**

- Do not build streaming audio delivery in this iteration.
- Do not support arbitrary user-uploaded cloning references through the service API.
- Do not claim robust emotion-tag support; only expose Chatterbox generation parameters.

## Decisions

### Keep Chatterbox as a separate Docker service

Chatterbox uses CUDA and significantly more VRAM than earlier CPU TTS experiments. A separate `docker/chatterbox-tts` Compose service lets users stop it when they need GPU memory.

Follow-up decision: after listening tests, the user rejected Piper/Kokoro quality and asked to remove Piper and other non-selected TTS experiment paths from the active project. Chatterbox is now the single retained local TTS backend.

### Reuse the OpenAI-style speech endpoint shape

The service will expose `POST /v1/audio/speech` with `text`, `voice`, and optional tuning parameters. This matches the existing local client contract, so Codex voice hooks and OpenClaw can call the same endpoint without Chatterbox-specific client code.

Alternative considered: create a bespoke `/synthesize` endpoint only. That would work for OpenClaw but require extra client branching.

### Package curated voice presets, not arbitrary cloning input

The first service version will provide fixed voice presets:

- `male`: built-in Chatterbox es-ES conditioning with neutral settings.
- `female`: Common Voice reference `common_voice_female_es_ref_01_row_410.wav` with the warm parameters selected by the user.

This keeps the API predictable and avoids exposing a general voice-cloning upload surface before consent, storage, and misuse controls are designed.

### Track simple in-process metrics

The service will expose JSON metrics rather than a Prometheus dependency. Metrics include total requests, failures, per-voice counts, last/average synthesis seconds, average realtime factor, and last observed VRAM if `nvidia-smi` is available.

Alternative considered: add `prometheus-client`. That is useful later but not necessary for the current local/offline integration.

## Risks / Trade-offs

- [Risk] Chatterbox package or model loading may change upstream. -> Pin the implementation to the same loading approach validated by the benchmark, including tolerant S3Gen loading for the es-ES pack.
- [Risk] First startup can be slow because model weights download and load. -> Keep a Docker volume for cache and make readiness explicit through `/health`.
- [Risk] GPU memory can collide with Whisper or other local AI services. -> Provide stop/status commands and document that stopping the container disables voice output without affecting text workflows.
- [Risk] Voice cloning quality depends on short Common Voice references. -> Ship only the user-selected preset now and keep future reference management out of scope.
