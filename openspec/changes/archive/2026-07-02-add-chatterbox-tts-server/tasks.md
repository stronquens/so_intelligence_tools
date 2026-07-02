## 1. Docker Service

- [x] 1.1 Add `docker/chatterbox-tts` service files.
- [x] 1.2 Package the selected Common Voice female reference preset.
- [x] 1.3 Implement Chatterbox es-ES model loading, voice selection, health, speech, and metrics endpoints.

## 2. CLI And Client Integration

- [x] 2.1 Add lifecycle methods for ensure, stop, status, and readiness.
- [x] 2.2 Add CLI commands for the Chatterbox TTS service.
- [x] 2.3 Ensure existing TTS clients can select `male` or `female` against the Chatterbox endpoint.

## 3. Documentation

- [x] 3.1 Document Chatterbox TTS setup, lifecycle, API, voices, metrics, and Codex/OpenClaw integration.
- [x] 3.2 Update index/getting-started documentation to point to the new service.

## 4. Validation

- [x] 4.1 Run static Python validation and focused tests.
- [x] 4.2 Build or smoke-test the Docker service enough to verify startup wiring.
- [x] 4.3 Record validation evidence and run OpenSpec strict validation.

## 5. Chatterbox-Only Cleanup And Codex Trial

- [x] 5.1 Remove Piper service code, commands, tests, and documentation from the active project path.
- [x] 5.2 Make Chatterbox the default local TTS target for generic Codex voice clients.
- [x] 5.3 Clean discarded TTS benchmark code, audio/model caches, containers, images, and volumes while keeping the deployed Chatterbox service assets.
- [x] 5.4 Smoke-test the Codex visible-event listener against Chatterbox and record evidence.
- [x] 5.5 Document Windows Chatterbox status, VRAM measurements, Qwen embeddings usage, and Whisper coexistence.

## 6. Windows Codex Wrapper Integration

- [x] 6.1 Add a Windows launcher for the Codex TTS wrapper and resolve the bundled Windows Codex CLI.
- [x] 6.2 Add native Windows WAV playback for local TTS output.
- [x] 6.3 Configure the VS Code/Codex extension `chatgpt.cliExecutable` setting to use the wrapper.
- [x] 6.4 Validate wrapper-to-listener-to-Chatterbox playback and record evidence.

## 7. Windows Codex Desktop Integration

- [x] 7.1 Add a Codex Desktop session JSONL monitor that speaks visible assistant messages through Chatterbox.
- [x] 7.2 Add CLI and hidden Windows Startup launcher support for the Desktop session monitor.
- [x] 7.3 Validate the monitor with a Codex Desktop-shaped session JSONL event and Chatterbox metrics.
- [x] 7.4 Start the monitor for the current Windows session and document the Desktop-specific integration path.
