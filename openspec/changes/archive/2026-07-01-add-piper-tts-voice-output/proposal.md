## Why

The local assistant can already listen through the warm Whisper Docker runtime, but it cannot speak back. A lightweight local TTS service would let visible Codex/assistant progress and responses be read aloud, while still allowing the user to disable speech simply by stopping or toggling the container.

Piper is the right first target for this CPU-only workstation because the July 1, 2026 benchmark showed it was the fastest Spanish-capable option by a large margin, with acceptable intelligibility and tiny retained audio artifacts.

## What Changes

- Add a warm Docker service for Piper TTS, modeled after the existing warm faster-whisper Docker setup.
- Expose a local HTTP TTS API that accepts text, voice, and basic synthesis options, then returns playable audio or streams/saves temporary audio for playback.
- Provide operational commands to start, stop, check readiness, and optionally install the Piper TTS service.
- Add a voice-output bridge that reads aloud visible assistant events and final messages from supported clients, starting with a Codex/VS Code integration path where events are available.
- Treat a stopped/unavailable TTS container as the explicit "voice output off" state: the application SHALL continue displaying text normally and SHALL NOT block workflows.
- Limit speech to visible UI/event text. Hidden model reasoning or private chain-of-thought SHALL NOT be requested, exposed, logged, or read aloud.
- Keep generated speech ephemeral by default and avoid retaining per-message audio unless explicit debug capture is enabled in a future change.

## Capabilities

### New Capabilities

- `local-tts-voice-output`: local text-to-speech output using a warm Piper Docker runtime, plus client-side controls for speaking visible assistant text aloud.

### Modified Capabilities

- None.

## Impact

- New Docker assets under `docker/` for Piper TTS.
- New Python runner/client code for local TTS requests, playback, readiness checks, and lifecycle commands.
- Potential CLI commands under `so-intelligence-tools` for install/start/stop/status.
- Potential desktop or VS Code/Codex integration hooks that subscribe to visible assistant events and forward selected text to the TTS service.
- Documentation for Linux operation, voice selection, toggle behavior, privacy boundary, and troubleshooting.
