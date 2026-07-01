## Why

The project has a local speech-to-text route for dictation, but no equivalent local text-to-speech service for OS-level voice output or future translated-voice workflows. Before choosing a default TTS backend, we need measured CPU performance and Spanish quality evidence across the models the user is considering.

## What Changes

- Research local TTS candidates for Spanish on a CPU-only Linux workstation.
- Compare Docker/service feasibility, model cleanup strategy, latency, quality, voice control, and licensing constraints.
- Prepare a benchmark spike that can run candidates in isolated containers or temporary caches without polluting the production Docker state.
- Candidate set:
  - Chatterbox Multilingual V3 and Spanish language packs.
  - Qwen3-TTS 0.6B and 1.7B variants.
  - Piper Spanish voices.
  - Kokoro 82M / Kokoro ONNX.
  - NeuTTS Nano Spanish.

## Capabilities

### New Capabilities

- `local-tts-api`: local text-to-speech service that can synthesize Spanish text to audio through an interchangeable backend.

### Modified Capabilities

None.

## Impact

- Benchmark/research artifacts under this OpenSpec change.
- Future Docker files and scripts may be added during implementation.
- No production runtime change until a candidate is benchmarked and selected.
