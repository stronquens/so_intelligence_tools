## Why

The dictation stack should be unambiguous when the project is pulled on another Linux machine: the supported ASR backend is the faster-whisper Docker server, and historical experimental runtime artifacts should not appear in active setup paths or repository search.

## What Changes

- Remove archived experimental dictation runtime artifacts that still referenced retired implementation paths.
- Add a Linux bootstrap command path that ensures `docker/whisper-server` has an `.env` file and is started with `docker compose up -d`.
- Wire the Whisper Docker startup into Linux desktop integration and standalone dictation service installation.
- Update Linux setup documentation so a fresh pull installs the Whisper path.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `push-to-talk-dictation`: Linux bootstrap SHALL prepare the faster-whisper Docker backend before enabling the dictation service.

## Impact

- Linux setup now requires Docker for dictation.
- Historical archives related to the retired runtime are removed from the repository.
- The active ASR path remains `PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http`.
