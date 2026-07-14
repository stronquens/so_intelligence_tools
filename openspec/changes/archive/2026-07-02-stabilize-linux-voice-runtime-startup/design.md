## Overview

Introduce a user-level `so-intelligence-tools-voice-runtimes.service` that runs once after graphical login and starts both Docker runtimes:

- `docker/whisper-server` for push-to-talk dictation on port `9000`;
- `docker/piper-tts` for Codex/assistant voice output on port `9010`.

The service is `Type=oneshot` with `RemainAfterExit=yes`, so dependent user services can order themselves after it without keeping an extra process alive.

## Details

- The existing `ensure_whisper_server()` and `ensure_piper_tts_server()` methods remain the runtime preparation primitives.
- A new installer method writes and enables the voice runtime service.
- The dictation user service gains `After=` and `Wants=` edges to the voice runtime service, so login startup first attempts to bring Docker runtimes up and only then starts the listener.
- The voice runtime service uses the repo CLI command `ensure-linux-voice-runtimes`.
- `docker/whisper-server/.env.example` includes `WHISPER_API_KEY=` because current `hwdsl2/whisper-server` images autogenerate an API key when `/var/lib/whisper` is a fresh mounted volume and the variable is absent. The local repo binds the service to `127.0.0.1`, so the default project client expects no auth.

## Non-Goals

- Do not manage Docker Desktop itself.
- Do not add Windows startup behavior in this change.
- Do not implement authenticated Whisper client requests.
