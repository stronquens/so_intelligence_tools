## 1. Runtime Startup Service

- [x] 1.1 Add an installer method for a Linux user `so-intelligence-tools-voice-runtimes.service`.
- [x] 1.2 Add a CLI command to ensure both Whisper and Piper runtimes.
- [x] 1.3 Add a CLI install command for the voice runtime startup service.
- [x] 1.4 Make the dictation listener service order itself after the voice runtime startup service.

## 2. Whisper Auth And Local Configuration

- [x] 2.1 Add `WHISPER_API_KEY=` to `docker/whisper-server/.env.example`.
- [x] 2.2 Ensure existing local `.env` gets the explicit empty `WHISPER_API_KEY` if missing.

## 3. Documentation

- [x] 3.1 Document automatic Linux voice runtime startup.
- [x] 3.2 Document the recovery commands for Docker context and runtime ensure.

## 4. Validation

- [x] 4.1 Add/update unit tests for service generation and env handling.
- [x] 4.2 Install/reload the user service on this Linux machine.
- [x] 4.3 Validate Whisper, Piper, and dictation service readiness after installation.
