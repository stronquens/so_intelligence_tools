# Getting Started On Linux

This guide installs the Linux desktop integration for `so_intelligence_tools`.

## Supported Baseline

Current development and validation targets:

- Linux desktop
- GNOME
- X11 session preferred for the most reliable text automation
- PulseAudio or PipeWire with PulseAudio compatibility tools
- Python managed by Poetry with an in-project `.venv`

Check your session type:

```bash
echo "$XDG_SESSION_TYPE"
```

For the most stable selected-text workflow, prefer:

```text
x11
```

## Install System Dependencies

```bash
make install-system-deps
```

The script installs desktop and audio tooling such as `xclip`, `xdotool`, `wl-clipboard`, `wtype`, `ydotool`, `libnotify-bin`, and `pulseaudio-utils`.

Docker is also required for push-to-talk dictation because the supported ASR backend is the faster-whisper server in `docker/whisper-server`.

Docker is also used for local text-to-speech voice output when the Piper service is enabled.

## Install Python Dependencies

```bash
poetry install
```

The repository uses `poetry.toml` to keep the virtual environment inside the project as `.venv`.

## Configure Environment

```bash
cp .env.example .env
```

For local Ollama inference:

```env
INFERENCE_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4-e2b-longctx:latest
LOCAL_INFERENCE_API_PORT=8010
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
```

Pull the default local model:

```bash
ollama pull gemma4-e2b-longctx:latest
```

## Install Desktop Integration

```bash
poetry run so-intelligence-tools install-linux-desktop-integration
```

This creates:

- `~/.config/systemd/user/so-intelligence-tools-api.service`
- `~/.config/systemd/user/so-intelligence-tools-push-to-talk-dictation.service`
- `~/.config/autostart/so-intelligence-tools-desktop-health.desktop`
- GNOME shortcuts for stable desktop tools
- `docker/whisper-server/.env` from `.env.example` if it does not exist
- a running `docker/whisper-server` faster-whisper container through `docker compose up -d`

The default Whisper container profile is CPU-oriented (`WHISPER_DEVICE=cpu`, `WHISPER_COMPUTE_TYPE=int8`). Machines with NVIDIA GPU support can opt into the CUDA override documented in [Faster-Whisper Docker Server](whisper-docker.md).

On CPU-only Linux, the current recommended Whisper model remains `large-v3-turbo`. A July 1, 2026 benchmark on the current i7-12700H workstation found `base` and `small` faster but too lossy for Spanish dictation, and `medium` only modestly faster with visible quality loss. See [Linux Whisper CPU Benchmark](whisper-cpu-benchmark-linux.md).

Default shortcuts:

| Tool | Shortcut |
| --- | --- |
| Correct selected text | `Ctrl + Alt + C` |
| Push-to-talk dictation | `Ctrl + Shift + Space` |
| System audio translation | `Ctrl + Alt + Y` |
| Voice translation virtual microphone | `Ctrl + Alt + U` |

To inspect the effective shortcut map after editing `.env`:

```bash
poetry run so-intelligence-tools show-shortcuts --platform linux
```

If `Ctrl + Space` still opens an input-method or launcher search bar, make sure the dictation service has restarted after the move to `Ctrl + Shift + Space`:

```bash
systemctl --user restart so-intelligence-tools-push-to-talk-dictation.service
```

The installer also clears known old `Ctrl + Space` IBus/GNOME and Ulauncher bindings where possible, but Linux desktop shortcuts are best-effort and can depend on the user's session.

## Verify Services

```bash
systemctl --user status so-intelligence-tools-api.service
systemctl --user status so-intelligence-tools-push-to-talk-dictation.service
curl http://127.0.0.1:9000/v1/models
curl http://127.0.0.1:8010/health
curl http://127.0.0.1:8010/status
```

Useful logs:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/desktop_health.log
tail -n 120 ~/.cache/so_intelligence_tools/selected_text_correction.log
tail -n 120 ~/.cache/so_intelligence_tools/system_audio_shortcut.log
tail -n 120 ~/.cache/so_intelligence_tools/voice_translation_logs/*.log
```

## Manual API Start

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010 --reload
```

## Docker Stack

```bash
docker compose up -d --build
docker compose exec ollama ollama pull gemma4-e2b-longctx:latest
curl http://127.0.0.1:8000/health
```

The desktop integration defaults to port `8010` to avoid conflicts with other local projects. Docker publishes the API on `8000`.

## Whisper Server

The dictation backend can also be started independently:

```bash
poetry run so-intelligence-tools ensure-whisper-docker-server
poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
```

See [Faster-Whisper Docker Server](whisper-docker.md) for GPU and CPU porting notes.

Linux dictation records while the shortcut is held, then sends the captured utterance to `/v1/audio/transcriptions` after release. The Docker server is warm, so the first dictation avoids model startup, but CPU transcription can still add a visible delay after release.

## Piper TTS Voice Output

Linux can also run a warm Piper text-to-speech container for reading visible Codex activity aloud:

```bash
poetry run so-intelligence-tools ensure-piper-tts-server
poetry run so-intelligence-tools status-piper-tts-server
poetry run so-intelligence-tools speak-text --text "Hola, esto es una prueba de voz local."
```

Stopping the Piper container disables voice output everywhere while leaving text workflows unchanged:

```bash
poetry run so-intelligence-tools stop-piper-tts-server
```

The default spoken detail for Codex is `actions`: task start/end plus tool, function and command lifecycle. Per-window controls can mute one VS Code/Codex window, change detail, or switch between the configured `male` and `female` Piper aliases:

```bash
poetry run so-intelligence-tools codex-voice-sessions
poetry run so-intelligence-tools codex-voice-off
poetry run so-intelligence-tools codex-voice-detail minimal
poetry run so-intelligence-tools codex-voice-voice female
```

See [Piper TTS Voice Output](piper-tts-voice-output.md) for the VS Code wrapper, multi-voice container configuration, privacy boundary and troubleshooting.
