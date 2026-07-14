## Context

`main` contains the Windows/GPU Chatterbox implementation and removed the older
Piper Docker assets. A separately developed Linux change assumed Piper and added
login-time startup for Whisper plus Piper. Applying either side globally breaks
the other: Chatterbox is not an appropriate unconditional CPU/Linux default,
while Piper must not replace the validated Windows Chatterbox workflow.

The existing TTS client already talks to an OpenAI-style local speech endpoint,
so backend selection can remain outside the event-reading and playback layers.

## Goals / Non-Goals

**Goals:**

- Resolve a configured `auto`, `piper`, `chatterbox`, or `none` backend with
  platform-aware defaults (`piper` on Linux and `chatterbox` on Windows).
- Restore the Linux Piper Docker service and its lifecycle commands.
- Start Whisper and the resolved Linux TTS backend from one user service after
  login, while avoiding automatic Chatterbox GPU allocation unless selected.
- Keep the existing Chatterbox commands, Windows startup flows and Codex voice
  event processing intact.
- Make the default local TTS URL follow the resolved backend unless explicitly
  overridden.

**Non-Goals:**

- Sharing model/voice configuration between Piper and Chatterbox.
- Installing Docker or GPU drivers.
- Automatically starting a Linux GPU backend merely because a GPU exists.
- Replacing existing Windows startup integration with systemd concepts.

## Decisions

### Use one backend selector with platform-aware `auto`

Add `LOCAL_TTS_BACKEND=auto|piper|chatterbox|none`. `auto` resolves from the
runtime platform, not from model discovery: Linux selects Piper, Windows selects
Chatterbox, and unsupported platforms select `none` with an actionable error for
explicit lifecycle commands.

This is preferred to separate Windows/Linux environment variables because it
keeps CLI and client configuration portable. Explicit values remain available
for Linux GPU hosts and development tests.

### Resolve the default URL from the selected backend

`LOCAL_TTS_BASE_URL` becomes an optional override. Without it, Piper resolves to
`http://127.0.0.1:9010` and Chatterbox to
`http://127.0.0.1:9011`. Client code continues to consume one HTTP API and does
not branch on platform.

This avoids starting Piper correctly while still sending speech to the former
Chatterbox port.

### Keep backend-specific lifecycle commands and add generic orchestration

Retain Chatterbox commands and restore equivalent Piper commands. Add generic
`ensure-local-tts-server` and Linux `ensure-linux-voice-runtimes` commands that
route through the selector. Backend-specific commands remain useful for
diagnostics and explicit operation.

### Make Linux login startup backend-aware

Install `so-intelligence-tools-voice-runtimes.service` as a Linux user oneshot.
It always ensures Whisper, then ensures only the configured TTS backend. `none`
starts no TTS service. Chatterbox is therefore never allocated on Linux login
unless explicitly configured.

The dictation listener orders itself after this service so Whisper readiness is
established before shortcuts are accepted.

### Restore Piper as a Linux-scoped implementation

Restore the previously validated Piper Compose service and documentation, but
label its support scope as Linux CPU. Chatterbox documentation remains the
Windows and optional Linux GPU path. Neither backend deletes or aliases the
other.

## Risks / Trade-offs

- **Existing `.env` pins `LOCAL_TTS_BASE_URL=9011` on Linux** → Document that an
  explicit URL overrides platform selection and update `.env.example` to leave
  the URL unset by default.
- **Piper assets may have drifted behind current client behavior** → Restore the
  last validated service, run API/client tests, and smoke its health endpoint
  when Docker is available.
- **Automatic Chatterbox startup consumes GPU memory** → `auto` never selects it
  on Linux; users must choose `LOCAL_TTS_BACKEND=chatterbox` explicitly.
- **Systemd service starts before Docker is ready** → retain bounded startup
  timeout and retry-on-failure behavior.
- **Backend voice aliases differ** → keep voice selection backend-owned and
  document validated aliases separately.

## Migration Plan

1. Restore Piper assets and backend lifecycle methods.
2. Add selector and URL resolution with unit tests for Linux and Windows.
3. Integrate the Linux voice-runtime service and dictation ordering.
4. Update environment examples and platform-specific documentation.
5. Validate focused Python tests, OpenSpec and Docker configuration.

Rollback is a normal revert of this change: Chatterbox files and commands are
not removed, so Windows remains on its previous behavior throughout.

## Open Questions

None blocking. Automatic Linux GPU detection is deliberately deferred in favor
of explicit configuration.
