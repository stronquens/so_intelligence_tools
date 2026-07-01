# Documentation

This folder contains the public documentation for `so_intelligence_tools`.

The project is Linux-first for audio-routing workflows, with working Linux CPU push-to-talk dictation through a warm faster-whisper Docker backend and a Linux-validated Piper TTS service for speaking visible Codex activity. Windows separately supports selected text correction, the main overlay launcher, shortcut introspection and push-to-talk dictation with Windows-specific Startup launchers and adapters. The architecture keeps operating-system adapters separate from shared use cases.

## Start Here

- [Getting Started On Linux](getting-started-linux.md)
- [Windows Support](windows-support.md)
- [Configuration](configuration.md)
- [Keyboard Shortcuts](keyboard-shortcuts.md)
- [Architecture](architecture.md)
- [Troubleshooting Linux](troubleshooting-linux.md)

## Capabilities

- [Selected Text Correction](selected-text-correction.md)
- [Screenshot OCR](screenshot-ocr.md)
- [System Audio Translation](system-audio-translation.md)
- [Voice Translation Virtual Microphone](voice-translation-virtual-microphone.md)
- [Windows Audio Routing Research](windows-audio-routing.md)
- [Push-To-Talk Dictation](push-to-talk-dictation.md)
- [Linux Whisper Dictation](linux-whisper-dictation.md)
- [Faster-Whisper Docker Server](whisper-docker.md)
- [Linux Whisper CPU Benchmark](whisper-cpu-benchmark-linux.md)
- [Piper TTS Voice Output](piper-tts-voice-output.md)
- [Linux Nemotron Streaming Dictation](nemotron-dictation-backup.md)
- [Desktop UI](desktop-ui.md)
- [Local Inference API](local-inference-api.md)

## Project And Safety

- [Security And Secrets](security-and-secrets.md)
- [OpenSpec Contribution Workflow](contributing-openspec.md)

## Status Labels

- `Working`: useful on a supported desktop today.
- `Experimental`: implemented but still being stabilized.
- `Planned`: specified or intended, but not yet polished for daily use.
