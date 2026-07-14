# Desktop UI

Status: Functional on Linux for realtime translation and useful on Windows for overlay launch/settings. Translator provider support remains platform-dependent.

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
- independent realtime translator window launched from `Ctrl + Alt + Y` on Linux or the `Traducir audio` tool card
- backend-driven source and target language selectors with real flag assets and functional swap
- aligned two-column transcript and translation timeline
- compact/comfortable message density persisted in local storage
- mock-faithful model popover listing only the two modes supported by Python
- meeting-style controls
- Electron preload bridge for desktop and translator commands
- live Python session state, partial text, grouped final blocks and mode updates
- functional pause, resume, restart, stop and translated-microphone controls
- real PCM-driven input meter; it shows system audio normally and the physical microphone while translated voice is active
- native close, minimize and maximize/restore controls with enlarged targets
- synchronized pending feedback for pause and resume
- synchronized pending/connected feedback for the translated microphone
- a persistent translated-voice output strip showing the backend routing message
- stationary large-button surfaces with only the inner pending glyph rotating
- responsive layouts down to the 900 x 600 supported minimum window size
- reduced-motion-safe transitions for incoming blocks and session states
- generated application icon in `assets/branding/app-icon.ico` and `desktop/assets/app-icon.png`

The translator starts a dedicated Python child process and exchanges one JSON event or command per line through standard streams. Python remains responsible for audio capture, providers, credentials, history and logs; the renderer never talks directly to a model provider. `stdout` is reserved exclusively for JSON Lines; human-readable state and diagnostic output belongs on `stderr` or in session logs. Electron records and ignores an isolated non-JSON stdout line so it cannot collapse an otherwise healthy live session. Selected-text correction is also wired through Electron to the Python CLI. Other unwired tool cards return clear pending feedback instead of silently doing nothing.

By default, the desktop app opens the overlay launcher. The launcher, settings and translator are separate Electron windows, so opening settings or translation does not replace the main launcher view. The launcher and settings windows are sized to their visible glass panels so transparent margins do not intercept clicks on neighboring windows.

The realtime translator view remains directly reachable for development with:

```text
?view=translator
```

Without the Electron preload bridge, that route deliberately renders a labelled preview with sample transcript data. Production Electron sessions start empty and display only events received from Python.

## Linux Shortcut And Fallback

`Ctrl + Alt + Y` executes `scripts/run-system-audio-translation-debug.sh`. The wrapper opens or alternates the single Electron translator window. If the local Electron dependency is unavailable, it falls back to the retained Tkinter UI:

```bash
poetry run so-intelligence-tools run-system-audio-translation-toggle
```

The connected bridge can be launched directly for diagnostics, but its stdout is a machine-readable JSON Lines stream:

```bash
poetry run so-intelligence-tools run-system-audio-translation-desktop-bridge
```

Redirect `stderr` separately when capturing bridge diagnostics. Mixing both
streams produces a file that is intentionally not valid JSONL.

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

For visual and responsive QA, use the explicit mock launcher. It never starts
the Python bridge or a provider session, so resizing, screenshots and animation
checks cannot consume paid API usage:

```bash
cd desktop
npm run build
npm run translator:mock
```

Use the normal `Ctrl + Alt + Y` flow only for functional integration checks
that intentionally require real audio and provider responses.

When the translated microphone is used, the strip above the bottom controls
shows whether its output is off, connecting, active, stopping or in error. Once
Python confirms the route, the same strip displays the operational message that
identifies the virtual microphone to select in the call application. As soon as
translated PCM is actually written, it also displays confirmed chunk and byte
counters; this distinguishes a connected session from one that has produced
real virtual-microphone output.

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

- Add settings for provider and audio device selection.
- Wire the remaining overlay tool cards to their production workflows.
