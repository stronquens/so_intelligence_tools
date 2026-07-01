## Summary

Validated that push-to-talk dictation now defaults to `Ctrl + Shift + Space` across Python settings, shortcut map output, desktop UI defaults, documentation, and OpenSpec specs. Also validated that the press-and-hold listener can parse and match shortcuts containing `Shift`.

## Checks

### Python focused tests

Command:

```bash
poetry run pytest tests/test_press_and_hold_listener.py tests/test_shortcut_map.py tests/test_windows_push_to_talk_dictation.py tests/test_user_services.py
```

Result:

```text
23 passed in 1.04s
```

Coverage:

- `_parse_shortcut` accepts `<ctrl>+<shift>+<space>` and `Ctrl + Shift + Space`.
- `PressAndHoldShortcutListener` starts/stops when Ctrl, Shift, and Space are pressed/released.
- Windows dictation service selects `WINDOWS_PUSH_TO_TALK_DICTATION_SHORTCUT=<ctrl>+<shift>+<space>`.
- Shortcut map uses the new Linux default and still supports configured Windows overrides.
- Existing Linux user service tests still pass with the prior Whisper service setup changes.

### Shortcut map CLI

Command:

```bash
poetry run so-intelligence-tools show-shortcuts --platform linux
poetry run so-intelligence-tools show-shortcuts --platform windows
poetry run so-intelligence-tools show-shortcuts --platform desktop
```

Result:

- Linux push-to-talk dictation: `<ctrl>+<shift>+<space>`.
- Windows push-to-talk dictation: `<ctrl>+<shift>+<space>`.
- Desktop push-to-talk dictation setting: `Ctrl + Shift + Space`.

### Desktop tests and build

Commands:

```bash
cd desktop
npm test
npm run build
```

Results:

```text
tests/App.test.ts: 15 passed
vite build and tsc -p tsconfig.electron.json completed successfully
```

Coverage:

- Vue settings/launcher tests pass with the new `Ctrl + Shift + Space` desktop settings value.
- Electron TypeScript compiles after updating the persisted settings migration from legacy `Ctrl + Space`, `Ctrl + Shift + D`, and `Ctrl + Alt + Space` values to `Ctrl + Shift + Space`.

### OpenSpec validation

Command:

```bash
openspec validate change-dictation-shortcut-to-ctrl-shift-space
```

Result:

```text
Change 'change-dictation-shortcut-to-ctrl-shift-space' is valid
```

## Residual Risk

- Running dictation services must be restarted or reinstalled to pick up the new default if they are already active.
- A user-local `.env` can still intentionally override the shortcut. No `PUSH_TO_TALK_DICTATION_SHORTCUT` or `WINDOWS_PUSH_TO_TALK_DICTATION_SHORTCUT` override lines were found in this workspace's `.env` during validation.
- The previous IBus `Ctrl + Space` cleanup remains in the Linux installer as best-effort cleanup for users who had the older default; it is no longer required for the active shortcut.
