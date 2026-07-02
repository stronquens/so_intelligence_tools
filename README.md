<p align="center">
  <img src="assets/branding/logo.png" alt="so_intelligence_tools logo" width="360">
</p>

<h1 align="center">so_intelligence_tools</h1>

<p align="center">
  Local-first AI tools that feel native inside your operating system.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Linux first" src="https://img.shields.io/badge/Linux-first-2ECC71?style=for-the-badge&logo=linux&logoColor=white">
  <img alt="Local first" src="https://img.shields.io/badge/Local--first-AI-7C3AED?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/status-experimental-F59E0B?style=for-the-badge">
</p>

---

`so_intelligence_tools` is a suite of AI-powered desktop tools for Linux and Windows, built around global keyboard shortcuts, local services, overlays, clipboard/text automation and realtime audio workflows.

The project is intentionally practical: open a desktop overlay, select text and fix it, capture a screen region and extract text, translate system audio, expose a translated virtual microphone to calls, or use local push-to-talk dictation.

## Table Of Contents

- [Highlights](#highlights)
- [Desktop UI](#desktop-ui)
- [Platform Support](#platform-support)
- [How It Works](#how-it-works)
- [Quick Start On Linux](#quick-start-on-linux)
- [Quick Start On Windows](#quick-start-on-windows)
- [Configuration](#configuration)
- [Keyboard shortcuts](docs/keyboard-shortcuts.md)
- [Roadmap](#roadmap)
- [Current Limitations](#current-limitations)
- [Development](#development)
- [Project Workflow](#project-workflow)
- [License](#license)

## Highlights

| Capability | What it does | Runtime | Status |
| --- | --- | --- | --- |
| Selected text correction | Correct selected text in any app while preserving the original language. | Both | 🟢 Useful now |
| Screenshot OCR | Capture a screen region and copy exact extracted text to the clipboard. | Planned | 🟡 Planned / specced |
| System audio translation | Listen to audio playing on the system and show live Spanish translation. | API | 🟢 Useful now |
| Desktop translation UI | Electron/Vue interface for realtime transcript and translation sessions. | Both | 🟡 In progress |
| Main overlay launcher | Electron/Vue overlay with tool cards, settings and Windows single-instance toggle. | Local | 🟢 Useful now on Windows |
| Translated virtual microphone | Expose `so_ai_translated_mic` to Slack/Meet/Zoom with passthrough or translated voice. | API | 🟢 Useful now |
| Push-to-talk dictation | Hold a shortcut and dictate text locally through a warm faster-whisper HTTP Docker server. | Local/on-prem | 🟢 Useful now on Linux and Windows |
| Local TTS voice output | Read Codex/OpenClaw progress aloud through a pausable Chatterbox es-ES GPU Docker service. | Local/on-prem | 🟡 Experimental on Windows |
| Local inference API | FastAPI gateway over Ollama or OpenAI-compatible remote providers. | Both | 🟢 Useful now |
| Overlay agent chat | Conversational OS tool launcher and assistant overlay. | Planned | 🔴 Roadmap |

Runtime legend: `Local/on-prem` runs without a third-party inference API, `API` currently depends on an external provider API, and `Both` can be configured for local or API-backed execution.

## Desktop UI

The Electron/Vue frontend now opens as the main overlay launcher by default. The overlay exposes tool cards, settings, shortcut rows and startup toggles; selected-text correction is wired through the Electron bridge, while remaining cards show clear pending feedback until connected. The realtime translation frontend remains available as a dedicated view with live status, language controls, transcript pairs, model selection and meeting-style controls.

<p align="center">
  <img src="assets/design/overlay-future-reference.jpg" alt="so_intelligence_tools overlay design reference" width="900">
</p>

## Platform Support

Status legend: 🟢 working/useful now, 🟡 partial or experimental, 🔴 not implemented yet.

| Feature | Linux | macOS | Windows |
| --- | :---: | :---: | :---: |
| Local inference API | 🟢 | 🟡 | 🟢 |
| Docker/Ollama backend | 🟢 | 🟡 | 🟡 |
| Global keyboard shortcuts | 🟢 | 🔴 | 🟢 |
| Selected text correction | 🟢 | 🔴 | 🟢 |
| Clipboard/text automation | 🟢 | 🔴 | 🟢 |
| System audio translation | 🟢 | 🔴 | 🔴 |
| Desktop overlay/settings UI | 🟡 | 🔴 | 🟢 |
| Desktop translation UI | 🟡 | 🔴 | 🟡 |
| Virtual translated microphone | 🟢 | 🔴 | 🔴 |
| Push-to-talk dictation | 🟢 | 🔴 | 🟢 |
| Local TTS voice output | 🟡 | 🔴 | 🟡 |

Linux remains the most complete target for audio routing and now has a working CPU-oriented push-to-talk dictation path through the warm faster-whisper Docker backend. Windows separately supports selected-text correction, hidden Startup launchers, the main overlay launcher, shortcut introspection, push-to-talk dictation with the same HTTP backend shape, and experimental Chatterbox TTS voice output for Codex Desktop, VS Code/Codex and OpenClaw HTTP integrations. The architecture keeps OS-specific code behind adapters so macOS and additional Windows capabilities can be added without rewriting the product model.

## How It Works

```text
Global shortcut / desktop UI
        ↓
Python tool runner
        ↓
OS adapters: Linux or Windows selection, clipboard, keyboard, notifications and platform-specific media adapters
        ↓
Local inference API or realtime ASR/audio provider
        ↓
Text, transcript, translated audio or virtual microphone output
```

The project currently uses:

- **Python + Poetry** for backend/tool runners.
- **FastAPI** for the local inference API.
- **Ollama** for local model serving.
- **LiteLLM/OpenAI-compatible providers** when a remote backend is configured.
- **OpenAI Realtime** for realtime audio translation workflows.
- **faster-whisper HTTP in Docker** for the preferred Linux and Windows dictation backend.
- **Chatterbox es-ES in Docker** for experimental local TTS voice output through a pausable GPU service.
- **PulseAudio/PipeWire compatibility tools** for audio routing on Linux.
- **Electron + Vue** for the main overlay, settings and desktop translation UI.
- **OpenSpec** for change proposals, specs, tasks and validation evidence.

## Quick Start On Linux

```bash
make install-system-deps
poetry install
poetry run so-intelligence-tools install-linux-desktop-integration
ollama pull gemma4-e2b-longctx:latest
```

The installer creates:

- `~/.config/systemd/user/so-intelligence-tools-api.service`
- `~/.config/systemd/user/so-intelligence-tools-push-to-talk-dictation.service`
- `~/.config/autostart/so-intelligence-tools-desktop-health.desktop`
- GNOME shortcuts for the stable desktop tools

Default shortcuts:

| Tool | Shortcut |
| --- | --- |
| Correct selected text | `Ctrl + Alt + C` |
| Push-to-talk dictation | `Ctrl + Shift + Space` |
| System audio translation | `Ctrl + Alt + Y` |
| Voice translation virtual microphone | `Ctrl + Alt + U` |

Detailed setup:

- [Documentation index](docs/README.md)
- [Getting started on Linux](docs/getting-started-linux.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting Linux](docs/troubleshooting-linux.md)
- [Windows support](docs/windows-support.md)
- [Security and secrets](docs/security-and-secrets.md)

## Quick Start On Windows

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry install
ollama pull gemma4-e2b-longctx:latest
poetry run so-intelligence-tools install-windows-api-startup
poetry run so-intelligence-tools install-windows-shortcut-listener-startup
poetry run so-intelligence-tools install-windows-dictation-startup
```

For the current session, start the API and listener manually or sign out and back in:

```powershell
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010
poetry run so-intelligence-tools listen-shortcuts
poetry run so-intelligence-tools listen-dictation-shortcut
```

Useful Windows shortcuts today:

| Tool | Shortcut |
| --- | --- |
| Open/toggle main overlay | `Ctrl + Alt + A` |
| Correct selected text | `Ctrl + Alt + C` |
| Push-to-talk dictation | `Ctrl + Shift + Space` |

Selected text correction tries to select and correct the whole focused text input when no text is selected. Dictation is validated with the faster-whisper HTTP Docker backend documented in [Faster-Whisper Docker Server](docs/whisper-docker.md). Windows Chatterbox TTS voice output is documented in [Windows Support](docs/windows-support.md) and [Chatterbox TTS Voice Output](docs/chatterbox-tts-voice-output.md), including Codex Desktop hooks, voice selection, latency measurements and VRAM coexistence with Whisper.

## Configuration

Copy `.env.example` to `.env` and add only the keys you actually need.

```bash
cp .env.example .env
```

Local Ollama example:

```env
INFERENCE_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4-e2b-longctx:latest
OLLAMA_WARMUP_ON_STARTUP=true
```

OpenAI-compatible remote provider example:

```env
INFERENCE_PROVIDER=litellm_proxy
LITELLM_PROXY_URL=https://your-litellm-proxy.example.com
LITELLM_VIRTUAL_KEY=...
LITELLM_MODEL=your/model
```

Realtime audio features require their own API key configuration. Keep real secrets in `.env`; the file is ignored by Git.

## Roadmap

### Now

- Collect more Linux CPU dictation samples with human references before changing the default Whisper model.
- Wire the remaining overlay tool cards to their production workflows.
- Improve debug traces for audio timing, ASR emissions and inserted text.
- Finish the realtime translation desktop UI flow.
- Keep hardening virtual microphone audio levels and call setup.

### Next

- Add screenshot OCR as a polished shortcut workflow.
- Connect persisted overlay shortcut settings to every OS-level listener where appropriate.
- Add runtime health checks for local models, realtime audio and virtual devices.

### Later

- macOS adapters for shortcuts, selection, clipboard and system audio.
- Broader Windows adapters for screenshots, audio routing and voice workflows.
- Local-only realtime voice translation backends.
- Overlay agent chat with access to selected text, screenshots and audio context.

## Current Limitations

- The project is Linux-first for audio-routing workflows, while Windows is already useful for selected-text correction, overlay launch/settings and push-to-talk dictation.
- Some audio workflows depend on PulseAudio/PipeWire compatibility tools such as `pactl`, `parec` and virtual sink/source modules.
- Push-to-talk dictation uses `Ctrl + Shift + Space` on Linux and Windows. Linux currently defaults to CPU `large-v3-turbo` and has local CPU benchmark evidence; Windows is validated separately with faster-whisper HTTP and Startup launchers.
- Realtime translation can require paid provider API keys depending on the selected backend.

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check src tests scripts
```

Run the local API manually:

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010 --reload
```

Run the Docker stack:

```bash
docker compose up -d --build
docker compose exec ollama ollama pull gemma4-e2b-longctx:latest
curl http://127.0.0.1:8000/health
```

## Project Workflow

This repository uses OpenSpec to keep product work explicit:

- proposals live in `openspec/changes/`
- accepted behavior lives in `openspec/specs/`
- completed work is archived with validation evidence

That makes the roadmap more than a wish list: every meaningful feature should have a proposal, design, tasks and validation trail.

## License

MIT. See [LICENSE](LICENSE).
