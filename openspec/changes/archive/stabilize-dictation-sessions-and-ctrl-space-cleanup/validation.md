## Summary

Validated that dictation runner sessions are serialized so a new press cannot start while the previous release is still finalizing. Also validated that the local machine has the faster-whisper HTTP server warm and the dictation listener active after restart. A later user report identified Ulauncher as the visible `Ctrl + Space` search bar; its hotkey was cleared and cleanup was added to the installer.

## Checks

### Focused tests

Command:

```bash
poetry run pytest tests/test_push_to_talk_dictation_session.py tests/test_user_services.py tests/test_press_and_hold_listener.py tests/test_shortcut_map.py tests/test_windows_push_to_talk_dictation.py
```

Result:

```text
29 passed in 0.87s
```

Coverage:

- Pressing again while `release()` is finalizing does not create a second capture.
- Existing post-roll, final-on-release insertion, shortcut parsing, shortcut map, Windows shortcut selection, and Linux user service tests still pass.
- Linux `Ctrl + Space` cleanup now covers IBus, GNOME input-source keybindings, and Ulauncher `hotkey-show-app` when those values are present.

Additional command after adding Ulauncher cleanup:

```bash
poetry run pytest tests/test_user_services.py tests/test_push_to_talk_dictation_session.py
```

Result:

```text
15 passed in 0.26s
```

### OpenSpec validation

Command:

```bash
openspec validate stabilize-dictation-sessions-and-ctrl-space-cleanup
```

Result:

```text
Change 'stabilize-dictation-sessions-and-ctrl-space-cleanup' is valid
```

### Runtime state observed locally

Commands:

```bash
systemctl --user show so-intelligence-tools-push-to-talk-dictation.service -p ActiveState -p SubState -p ExecMainPID
curl -fsS http://127.0.0.1:9000/v1/models
docker compose -f docker/whisper-server/compose.yaml ps
systemctl --user restart so-intelligence-tools-push-to-talk-dictation.service
```

Observed:

- Dictation listener was active and running.
- Whisper HTTP returned model `large-v3-turbo`.
- Docker showed `whisper-server` up on `127.0.0.1:9000`.
- Listener restarted successfully and remained active with a new PID.

### Ulauncher Ctrl Space search bar

Observed before cleanup:

```text
~/.config/ulauncher/settings.json: "hotkey-show-app": "<Primary>space"
~/.local/share/ulauncher/last.log: Trying to bind app hotkey: <Primary>space
```

Actions:

- Backed up Ulauncher settings to `/tmp/ulauncher-settings.before-codex.json`.
- Set `~/.config/ulauncher/settings.json` `hotkey-show-app` to an empty string.
- Stopped the running Ulauncher process.

Observed after cleanup:

```text
~/.config/ulauncher/settings.json: "hotkey-show-app": ""
pgrep -af ulauncher: no live Ulauncher process
```

## Residual Risk

- `faster_whisper_http` remains buffered-on-release, not true live streaming. The server is warm, but final transcription latency still depends on utterance length, hardware, and the selected Whisper profile.
- Global keyboard listeners cannot reliably prevent every desktop-shell shortcut from appearing. The practical mitigation is the `Ctrl + Shift + Space` default, service restart, and best-effort cleanup of known old `Ctrl + Space` bindings.
- Ulauncher may need to stay stopped or be restarted from a clean login/session environment. If it is relaunched, the empty `hotkey-show-app` setting should prevent `Ctrl + Space` from opening its search bar.
