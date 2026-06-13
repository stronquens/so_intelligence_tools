# Desktop UI

Status: In progress.

The desktop UI is an Electron/Vue frontend for realtime transcript and translation sessions.

## Location

```text
desktop/
```

## Current State

The UI currently includes:

- realtime translator shell
- language controls
- transcript and translation timeline
- model selection UI
- meeting-style controls
- Electron preload bridge for UI commands

Backend integration is still in progress. The current Electron bridge accepts mock commands.

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

## Build And Test

```bash
cd desktop
npm run test
npm run build
```

## Screenshot

The README screenshot lives at:

```text
assets/screenshots/realtime-translator-ui.png
```

## Next Work

- Wire live events from the translation process into the UI.
- Replace mock command handling with real session control.
- Add settings for source, target, provider, and audio device selection.

