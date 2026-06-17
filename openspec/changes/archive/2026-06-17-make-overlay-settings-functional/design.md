## Storage

Electron main owns persistence because it has stable access to the local filesystem and OS app paths. Settings are stored as JSON under `app.getPath("userData")`.

The first schema is intentionally small:

- `shortcuts`: ordered shortcut rows shown in the overlay settings panel
- `startAtLogin`: visible startup preference
- `overlayAlwaysVisible`: visible overlay preference

Renderer code uses the same TypeScript model, but Electron validates and normalizes incoming payloads before writing to disk.

## Bridge Contract

The existing `desktop-command` IPC channel is extended with:

- `get-settings`
- `save-settings`

Both return the existing structured result envelope and include `settings` on success. This keeps the renderer bridge small and avoids adding a second preload API for the same desktop control surface.

## Shortcut Editing

Shortcut rows use an edit button. Once editing, the row accepts either:

- a keyboard event, captured and normalized as `Ctrl + Alt + C`
- direct text entry, useful for development and tests

The renderer checks duplicate assignments before saving. Electron also validates that shortcut values are non-empty strings before persisting.

## Runtime Binding Boundary

This change persists the settings and makes the UI functional. The existing Python Windows listener is a separate resident process and is not live-reloaded by Electron yet. A later change should decide whether the Python listener reads the same JSON at startup, watches it, or whether Electron owns global shortcut registration.
