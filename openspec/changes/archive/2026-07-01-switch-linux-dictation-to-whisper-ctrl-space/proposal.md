## Why

Linux dictation should match the newly documented Whisper path: a warm faster-whisper Docker backend and a simple press-and-hold shortcut. This change originally moved Linux from `Ctrl + Alt + Space` to `Ctrl + Space`; the active default is now superseded by `change-dictation-shortcut-to-ctrl-shift-space`, which uses `Ctrl + Shift + Space` to avoid OS collisions.

## What Changes

- Change the Linux push-to-talk dictation default shortcut away from the old `Ctrl + Alt + Space` binding.
- Keep `faster_whisper_http` as the default dictation runtime.
- Ensure the Linux desktop installer starts the faster-whisper Docker server before enabling the dictation listener.
- During Linux desktop setup, clear known Ubuntu/IBus `Ctrl + Space` hotkeys when present.
- Update docs and examples to show the current Linux Whisper dictation shortcut.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `push-to-talk-dictation`: Linux dictation uses Whisper/faster-whisper HTTP by default and is triggered by the configured press-and-hold shortcut.
- `keyboard-shortcuts`: Linux shortcut documentation and setup describe the current dictation shortcut.

## Impact

- Linux dictation service setup and defaults change.
- Documentation and `.env.example` change.
- No Nemotron runtime is restored; it remains documented as a rollback/reference path.
