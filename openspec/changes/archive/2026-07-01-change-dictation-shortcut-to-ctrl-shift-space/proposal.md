## Why

`Ctrl + Space` is too easy to trigger while typing and conflicts with operating-system search/input-method shortcuts. Push-to-talk dictation needs a less collision-prone default that still feels quick to press.

## What Changes

- Change the default push-to-talk dictation shortcut from `Ctrl + Space` to `Ctrl + Shift + Space` on Linux and Windows.
- Update shortcut introspection, desktop UI defaults, persisted settings migration, examples, and documentation to show the new default.
- Add explicit `Shift` handling to the press-and-hold listener so the new shortcut is parsed and matched reliably.
- Stop treating Ubuntu/IBus `Ctrl + Space` cleanup as required for the active dictation default.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `push-to-talk-dictation`: default activation shortcut changes to `Ctrl + Shift + Space`.
- `keyboard-shortcuts`: effective shortcut maps and platform shortcut documentation change for dictation.
- `overlay-settings`: desktop settings defaults and legacy migration change for the dictation shortcut.

## Impact

- Python settings, press-and-hold shortcut parsing, shortcut map output, and related tests.
- Electron/Vue desktop settings defaults and migration behavior.
- Public docs, `.env.example`, OpenSpec delta specs, and validation evidence.
