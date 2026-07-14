## Why

The repository currently treats the Windows/GPU Chatterbox migration as if it
replaced the Linux Piper path globally. The two environments have different
hardware and operational needs: Windows uses the validated Chatterbox workflow,
while this Linux CPU-oriented workstation needs the lightweight Piper runtime
and must retain automatic Whisper startup after login.

## What Changes

- Restore Piper as a supported Linux CPU TTS backend without changing the
  validated Windows Chatterbox integration.
- Make runtime selection explicit by operating system and configuration instead
  of assuming one TTS backend for every host.
- Add a Linux user service and CLI workflow that starts Whisper plus the
  configured Linux TTS runtime after login.
- Keep Chatterbox available on Linux only when explicitly selected, avoiding an
  automatic GPU allocation by default.
- Restore Linux-specific Piper documentation and clearly separate it from the
  Windows/GPU Chatterbox documentation.
- Preserve existing commands where practical; no intentional breaking CLI or
  API change is introduced.

Non-goals:

- Replacing the validated Windows Chatterbox service.
- Making Piper the default on Windows.
- Automatically starting Chatterbox on every Linux login.
- Unifying Piper and Chatterbox model or voice configuration formats.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `local-tts-voice-output`: define platform-aware backend availability and Linux
  login startup behavior without weakening the Windows Chatterbox contract.
- `local-tts-api`: replace the global Chatterbox endpoint default with the
  platform-aware endpoint selected by the shared backend resolver.
- `push-to-talk-dictation`: ensure the Linux login runtime service prepares the
  local Whisper backend independently of the selected TTS provider.

## Impact

- Linux service installation and runtime orchestration in
  `infrastructure/user_services.py` and the CLI.
- Piper Docker assets restored for Linux and Chatterbox Docker assets retained.
- TTS configuration and command behavior across Linux and Windows.
- Linux getting-started, dictation, Piper and Chatterbox documentation.
- Unit tests for platform/backend routing, service generation and environment
  preparation.
