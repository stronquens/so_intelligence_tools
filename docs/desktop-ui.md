# Desktop UI

Status: Useful on Windows for overlay launch/settings and opening the translator shell; translator visuals and live backend wiring still need more polish.

The desktop UI is an Electron/Vue frontend for the system overlay and realtime transcript and translation sessions.

## Location

```text
desktop/
```

## Current State

The UI currently includes:

- overlay launcher based on `assets/design/overlay-future-reference.jpg`
- independent overlay settings window for shortcut rows and startup toggles
- persisted desktop settings through Electron `desktop-settings.json`
- Windows single-instance overlay toggle behavior
- real selected-text correction dispatch from the overlay
- independent realtime translator shell window launched from the `Traducir audio` tool card
- language controls
- transcript and translation timeline
- model selection UI
- meeting-style controls
- Electron preload bridge for desktop commands
- generated application icon in `assets/branding/app-icon.ico` and `desktop/assets/app-icon.png`

Backend integration is incremental. Selected-text correction is wired through Electron to the Python CLI; unwired tool cards return clear pending feedback instead of silently doing nothing.

By default, the desktop app opens the overlay launcher. The launcher, settings and translator are separate Electron windows, so opening settings or translation does not replace the main launcher view. The launcher and settings windows are sized to their visible glass panels so transparent margins do not intercept clicks on neighboring windows.

The realtime translator view remains directly reachable for development with:

```text
?view=translator
```

## Windows Shortcut

On the current Windows setup, the main overlay is opened or toggled with:

```text
Ctrl + Alt + A
```

The settings UI displays this shortcut as `Abrir overlay`. The planned Assistant action is intentionally unassigned by default so it does not collide with the overlay launcher.

The current desktop shortcut on this Windows machine is:

```text
D:\Users\Armando\Desktop\so_intelligence_tools Overlay.lnk
```

It points to the local Electron runtime and uses `assets/branding/app-icon.ico` as the Windows icon.

## Development

```bash
cd desktop
npm install
npm run dev
```

In another terminal:

```bash
cd desktop
npm run electron:dev
```

`desktop/.npmrc` keeps npm installs local to the desktop package. Dependencies should live in `desktop/node_modules/`; do not install frontend dependencies globally for this project.

Python dependencies are managed from the repository root with Poetry. `poetry.toml` sets `virtualenvs.in-project = true`, so Poetry creates and uses the repository-local `.venv/`.

## Build And Test

```bash
cd desktop
npm run test
npm run build
```

## Screenshot

The README design image lives at:

```text
assets/design/overlay-future-reference.jpg
```

## Future Overlay Design Reference

The future overlay visual direction is stored at:

```text
assets/design/overlay-future-reference.jpg
```

Use it as product guidance for the launcher grid, glass-style overlay surface, settings access, and shortcut configuration layout. It is not a pixel-perfect implementation contract.

## Next Work

- Wire live events from the translation process into the UI.
- Replace mock command handling with real session control.
- Bring the translator visual language closer to the main overlay/settings glass design.
- Add settings for source, target, provider, and audio device selection.
- Wire the remaining overlay tool cards to their production workflows.

