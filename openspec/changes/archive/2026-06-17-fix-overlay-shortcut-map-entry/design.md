# Design

The change is a correction to the shortcut registry and desktop defaults rather than a new listener.

## Approach

- Add a Windows shortcut map entry for `Open overlay` using `Ctrl + Alt + A`, with the mechanism described as the Windows shell/Electron launcher shortcut.
- Change the desktop overlay default shortcut for `open-overlay` from `Ctrl + Space` to `Ctrl + Alt + A`.
- Change the desktop Assistant default from `Ctrl + Alt + A` to `Sin asignar` so the settings UI does not show a conflict.
- Add a narrowly scoped migration in Electron settings sanitization:
  - when `open-overlay` is still the old default `Ctrl + Space`
  - and `assistant` is still the old default `Ctrl + Alt + A`
  - migrate those two values to the corrected defaults.

This keeps customized settings stable while fixing existing installs that only inherited the previous defaults.
