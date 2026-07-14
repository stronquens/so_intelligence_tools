## Why

The new Electron/Vue overlay already shows a `Traducir audio` tool card, and the new translator UI exists as `TranslatorView`, but the two are not connected. Clicking the card currently goes through generic tool dispatch and receives pending feedback instead of opening the new desktop translation experience.

## What Changes

- Link the overlay `Traducir audio` card to the new Electron/Vue translator view.
- Open the translator as a separate Electron window instead of replacing the launcher.
- Keep this inside the desktop app boundary instead of invoking the original Linux translation UI or CLI path.
- Add tests that prove the overlay opens the new translator view.

## Capabilities

### Modified Capabilities

- `overlay-launcher-desktop-ui`: the audio translation card opens the new translator view without closing the launcher.
- `realtime-translation-desktop-ui`: the new translator view becomes reachable from the overlay launcher.

## Impact

- Affects `desktop/electron/main.ts`, `desktop/src/OverlayLauncher.vue`, and desktop tests.
- Does not yet connect the translator view to live Windows audio capture or translation runtime.
