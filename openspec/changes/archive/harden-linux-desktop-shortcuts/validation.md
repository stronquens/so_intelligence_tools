# Validation

## Runtime Checks

- `127.0.0.1:8000` was occupied by another local Python backend.
- `127.0.0.1:8010` was assigned to `so_intelligence_tools`.
- `curl http://127.0.0.1:8010/status` returned `local-inference-api` status successfully.
- `systemctl --user status org.gnome.SettingsDaemon.MediaKeys.service` was restored to `active`.

## Shortcut Smoke Tests

`Ctrl + Alt + C` invoked:

- `scripts/run-selected-text-correction-debug.sh`
- `~/.cache/so_intelligence_tools/selected_text_correction.log`
- `POST http://127.0.0.1:8010/v1/text/generate`

Observed correction:

```text
voya comprovar atajo de correccion
Voy a comprobar el atajo de corrección.
```

`Ctrl + Alt + Y` invoked:

- `scripts/run-system-audio-translation-debug.sh`
- `~/.cache/so_intelligence_tools/system_audio_shortcut.log`
- `run-system-audio-translation-toggle`

## Persistence Checks

Installed files:

- `~/.config/systemd/user/so-intelligence-tools-api.service`
- `~/.config/autostart/so-intelligence-tools-desktop-health.desktop`

The desktop health script executed successfully and logged:

```text
starting-api-service
refreshing-gnome-media-keys
reinstalling-shortcuts
desktop-health completed
```

## Automated Tests

```bash
poetry run pytest -q
```

Result:

- `68 passed`
