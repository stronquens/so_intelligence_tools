## 1. Backend Selection

- [x] 1.1 Add validated `auto`, `piper`, `chatterbox`, and `none` backend resolution with Linux and Windows defaults.
- [x] 1.2 Resolve the default local speech URL from the selected backend while preserving explicit URL overrides.
- [x] 1.3 Add unit coverage for platform defaults, explicit overrides, and invalid backend values.

## 2. Piper And Runtime Lifecycle

- [x] 2.1 Restore the Linux Piper Docker service and backend-specific ensure, stop, status, and health behavior.
- [x] 2.2 Add generic local-TTS and Linux voice-runtime CLI commands that route to the configured backend.
- [x] 2.3 Add the Linux voice-runtime user service, Whisper environment repair, and dictation service ordering.
- [x] 2.4 Verify that Linux `auto` starts Whisper plus Piper, explicit Chatterbox starts Whisper plus Chatterbox, and `none` starts only Whisper.

## 3. Platform Documentation And Specs

- [x] 3.1 Restore Piper documentation as the Linux CPU path and retain Chatterbox documentation for Windows and optional Linux GPU use.
- [x] 3.2 Update environment examples, Linux setup, dictation, architecture, and troubleshooting documentation with backend selection and ports.
- [x] 3.3 Synchronize the implemented platform-aware requirements into the live specs.

## 4. Validation

- [x] 4.1 Run focused configuration, user-service, CLI, TTS client, and Codex voice tests.
- [x] 4.2 Run Ruff, Python compile checks, Docker Compose config checks, and strict OpenSpec validation.
- [x] 4.3 Record durable validation evidence and residual risks in `validation.md`.
