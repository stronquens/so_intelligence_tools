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
OLLAMA_MODEL=gemma4:e2b-it-qat
LOCAL_INFERENCE_API_PORT=8010
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
```

Pull the default local model:

```bash
ollama pull gemma4:e2b-it-qat
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

Default shortcuts:

| Tool | Shortcut |
| --- | --- |
| Correct selected text | `Ctrl + Alt + C` |
| Push-to-talk dictation | `Ctrl + Alt + Space` |
| System audio translation | `Ctrl + Alt + Y` |
| Voice translation virtual microphone | `Ctrl + Alt + U` |

## Verify Services

```bash
systemctl --user status so-intelligence-tools-api.service
systemctl --user status so-intelligence-tools-push-to-talk-dictation.service
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
docker compose exec ollama ollama pull gemma4:e2b-it-qat
curl http://127.0.0.1:8000/health
```

The desktop integration defaults to port `8010` to avoid conflicts with other local projects. Docker publishes the API on `8000`.

