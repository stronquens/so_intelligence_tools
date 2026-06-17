# Architecture

`so_intelligence_tools` is a local desktop automation suite. The core idea is simple: global shortcuts or desktop UI controls call small Python runners, those runners interact with operating-system adapters, and inference is handled by a local API or a realtime provider.

```text
Shortcut / desktop UI
        |
        v
Python CLI and tool runner
        |
        v
OS adapters: Linux or Windows selection, clipboard, keyboard, notifications, and platform-specific media adapters
        |
        v
Local inference API, local ASR runtime, or realtime provider API
        |
        v
Corrected text, OCR text, translated transcript, translated audio, or virtual microphone
```

## Main Layers

### Local Inference API

The FastAPI service in `src/local_inference_api/` exposes OpenAI-shaped endpoints for text generation and image text extraction. It can use:

- Ollama for local/on-prem model serving.
- LiteLLM or another OpenAI-compatible proxy for remote inference.

### Tool Runners

The package in `src/so_intelligence_tools/` contains the CLI, application use cases, infrastructure adapters, and feature-specific modules.

Important CLI commands include:

```bash
poetry run so-intelligence-tools run-selected-text-correction
poetry run so-intelligence-tools run-system-audio-translation-toggle
poetry run so-intelligence-tools run-voice-translation-virtual-mic-toggle
poetry run so-intelligence-tools run-push-to-talk-dictation-service
poetry run so-intelligence-tools listen-dictation-shortcut
poetry run so-intelligence-tools show-shortcuts
```

### Desktop Adapters

Adapters isolate OS-specific behavior from shared application use cases.

Linux, mainly GNOME/X11, currently covers:

- text selection and clipboard
- keyboard insertion
- screenshots
- desktop notifications
- GNOME custom shortcuts
- PulseAudio/PipeWire-compatible audio routing

Windows currently covers:

- Win32 clipboard read/write
- Win32 keyboard copy/paste automation
- selected text correction through clipboard roundtrips
- native global shortcut listener through `RegisterHotKey`
- push-to-talk dictation through a press-and-hold keyboard hook
- microphone capture through PortAudio / `sounddevice`
- faster-whisper HTTP dictation against a warm Docker server
- user Startup launchers for the API, shortcut listener and dictation listener
- Electron overlay launcher and settings on the desktop

### Audio Workflows

Audio features currently use different runtime strategies:

- System audio translation uses system audio capture and either chunked transcription or OpenAI Realtime.
- Voice translation virtual microphone uses realtime provider audio and PulseAudio virtual source routing.
- Push-to-talk dictation uses the `faster_whisper_http` ASR runtime against a warm Docker server; the earlier Nemotron ONNX route was removed after Whisper produced better Spanish dictation.

### Desktop UI

The Electron/Vue app under `desktop/` opens as the main overlay launcher by default and also contains the realtime translation view. The overlay has persisted settings, shortcut rows, startup toggles, single-instance Windows toggle behavior and a real bridge for selected-text correction. Some tool cards still return pending feedback until their production workflows are connected.

## Portability

Linux is still the most complete target for audio routing. Windows is supported for selected text correction, overlay launch/settings and push-to-talk dictation. The architecture keeps OS behavior behind adapters so macOS and broader Windows support can be added without replacing the product model.

