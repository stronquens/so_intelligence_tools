## Why

The overlay is visually close to the intended design, but interaction feedback is too static. Some placeholder tool cards also show the low-level `desktopBridge` unavailable message when clicked outside a fully wired Electron command path, which is confusing for tools that are not connected yet.

## What Changes

- Add hover, press and entrance motion to overlay cards, icon buttons, settings rows and panels.
- Keep motion subtle and fast so the overlay remains utility-like.
- Show placeholder/pending feedback for tool cards that are not wired yet instead of exposing `desktopBridge` internals.
- Preserve the real bridge error only for tools that actually need the desktop bridge now.
- Add a compact app icon derived from the overlay mark and use it for Electron windows, the built favicon and the Windows desktop shortcut.

## Capabilities

### Modified Capabilities

- `overlay-launcher-desktop-ui`: richer interactive states and clearer fallback feedback.

## Impact

- Affects `desktop/electron/`, `desktop/src/`, `desktop/index.html`, app branding assets, Windows shortcut metadata, and desktop tests.
- Does not add new backend tool wiring.
