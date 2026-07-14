## 1. Implementation

- [x] 1.1 Change Linux dictation default shortcut away from `Ctrl + Alt + Space`.
- [x] 1.2 Add best-effort cleanup for native Ubuntu/IBus `Ctrl + Space` hotkeys during Linux desktop integration.
- [x] 1.3 Update tests for defaults, service install, and shortcut map.

## 2. Documentation

- [x] 2.1 Update `.env.example` and Linux docs to remove `Ctrl + Alt + Space` as the active Linux default.
- [x] 2.2 Keep Nemotron documented only as backup/experimental rollback.
- [x] 2.3 Document CPU and GPU Whisper container profiles.

## 3. Validation

- [x] 3.1 Run targeted tests for user services, config, shortcut map, and dictation.
- [x] 3.2 Validate the OpenSpec change.
- [x] 3.3 Verify local docs links.
- [x] 3.4 Install/restart the Linux dictation service and verify the Whisper CPU backend is ready.
