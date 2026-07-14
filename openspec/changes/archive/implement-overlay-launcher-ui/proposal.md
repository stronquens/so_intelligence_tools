# Implement Overlay Launcher UI

## Problem

The project has a visual reference for the application overlay, but the Electron/Vue desktop app currently renders the realtime translator window by default. The overlay needs its own implemented capability that matches the provided launcher/settings design direction.

## Scope

- Add a new Electron/Vue overlay launcher view.
- Keep the existing realtime translator UI available as a separate view.
- Match the provided mockup's structure: translucent desktop scene, main launcher panel, settings panel, eight tool cards, shortcut controls, toggles, and footer shortcut hint.
- Keep the first iteration visual-only except for opening the settings panel from the launcher settings button.
- Use Lucide icons already available in the desktop package.
- Add tests for the new overlay and preserved translator view.

## Non-Goals

- Wire every overlay button to real tool execution in this change.
- Implement persisted shortcut editing.
- Implement OS-level transparent window behavior or always-on-top behavior.
- Replace Python runners or shortcut logic.
