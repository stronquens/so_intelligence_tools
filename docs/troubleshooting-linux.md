# Troubleshooting Linux

This guide collects the main Linux integration issues found during development.

## Shortcuts Do Nothing

Check whether GNOME media keys are alive:

```bash
systemctl --user status org.gnome.SettingsDaemon.MediaKeys.service
```

Refresh the desktop integration:

```bash
~/.config/autostart/so-intelligence-tools-desktop-health.desktop
```

Or run:

```bash
scripts/ensure-linux-desktop-integration.sh
```

Logs:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/desktop_health.log
```

## Selected Text Is Not Replaced

Prefer an X11 session for now:

```bash
echo "$XDG_SESSION_TYPE"
```

Run the action manually:

```bash
poetry run so-intelligence-tools run-selected-text-correction --debug
tail -n 120 ~/.cache/so_intelligence_tools/selected_text_correction.log
```

Common causes:

- the focused app does not expose selection reliably
- Wayland virtual keyboard support is missing
- clipboard content was not updated
- the local API is not the service listening on the configured port

## Port 8000 Or 8010 Conflict

Check listeners:

```bash
ss -ltnp '( sport = :8000 or sport = :8010 )'
curl http://127.0.0.1:8010/status
```

The desktop service defaults to `8010`; Docker publishes `8000`.

## Ollama Model Not Ready

```bash
ollama list
ollama pull gemma4:e2b-it-qat
curl http://127.0.0.1:8010/status
```

If `/status` is degraded, check the configured model name in `.env`.

## System Audio Translation Does Not Start

Check:

```bash
which pactl
which parec
pactl info
tail -n 120 ~/.cache/so_intelligence_tools/system_audio_shortcut.log
```

For realtime mode, verify the API key:

```env
OPENAI_API_KEY=...
SYSTEM_AUDIO_TRANSLATION_MODE=translate_es_openai_realtime
```

## Virtual Microphone Echo

Use this call setup:

```text
Microphone: so_ai_translated_mic
Speaker: headphones / normal output
```

Do not use the virtual microphone as speaker output.

Recommended volume baseline:

```env
VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03
VOICE_TRANSLATION_OUTPUT_VOLUME=0.75
```

## Push-To-Talk Dictation Misses Words Or Reorders Text

This is a known experimental limitation. See [Push-To-Talk Dictation](push-to-talk-dictation.md).

For now:

- start speaking slightly after pressing the shortcut
- avoid important fields until insertion is stabilized
- restart the user service after changing `.env`

```bash
systemctl --user restart so-intelligence-tools-push-to-talk-dictation.service
```

