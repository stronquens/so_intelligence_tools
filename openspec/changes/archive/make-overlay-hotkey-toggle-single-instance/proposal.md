## Why

The Windows shortcut opens a new Electron process every time it is pressed. The overlay should behave like a desktop utility: one running instance, with subsequent shortcut launches toggling the existing window instead of creating unlimited instances.

## What Changes

- Add Electron single-instance locking.
- Keep a reference to the main overlay window.
- On a second launch, toggle the existing window:
  - if visible and not minimized, minimize it to the taskbar
  - if hidden or minimized, restore/show/focus it centered on the active display
- Preserve existing first-launch behavior.

## Capabilities

### Modified Capabilities

- `overlay-launcher-desktop-ui`: overlay launch via OS shortcut becomes single-instance and toggle-style.

## Impact

- Affects `desktop/electron/main.ts`.
- Does not replace the Windows `.lnk` shortcut.
- Does not yet register global shortcuts from inside Electron.
