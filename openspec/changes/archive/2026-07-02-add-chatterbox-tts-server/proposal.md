## Why

Earlier local TTS services were operationally convenient but the user rejected their voice quality. The Chatterbox es-ES benchmark found a better candidate voice, so the project needs a Dockerized Chatterbox runtime that can stay warm, be stopped to release GPU VRAM, and be consumed by both Codex voice hooks and OpenClaw.

## What Changes

- Add a Dockerized Chatterbox es-ES TTS service with warm model loading.
- Expose a local HTTP speech API compatible with the existing `LocalTtsClient` shape.
- Provide parametric voice selection with at least:
  - `male`: built-in Chatterbox es-ES conditioning.
  - `female`: Common Voice reference clone selected by the user, `cv_female_es_ref_01` with warm settings.
- Expose health and metrics endpoints for readiness, voice metadata, request counts, latency, realtime factor, and VRAM observations.
- Add CLI lifecycle commands to start, stop, and check the Chatterbox TTS server, mirroring the warm local service pattern.
- Preserve operational documentation and validation evidence.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `local-tts-api`: the local TTS service shape now includes a concrete Chatterbox backend option with health/metrics and per-request voice selection.
- `local-tts-voice-output`: voice output uses a pausable GPU-backed Chatterbox runtime while keeping text workflows non-blocking when stopped.

## Impact

- New Docker service under `docker/chatterbox-tts/`.
- New local TTS reference audio assets for the chosen female voice.
- New CLI lifecycle commands and service installer methods.
- Existing Codex voice hooks target the new service through `LOCAL_TTS_BASE_URL`.
- OpenClaw can call the same HTTP API or lifecycle commands without depending on Codex internals.
- Requires Docker with NVIDIA GPU support for the intended low-latency path; CPU fallback is not a goal for this change.
- Removes the prior Piper service implementation and discarded TTS benchmark artifacts from the active project path after user selection.
