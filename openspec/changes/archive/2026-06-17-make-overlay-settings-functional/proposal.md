## Why

The overlay settings panel currently looks correct but is not functional. The user needs to edit keyboard combinations from the app instead of changing hardcoded values or restarting development code.

## What Changes

- Add a persisted desktop settings model for overlay shortcuts and simple startup preferences.
- Expose settings load/save through the Electron desktop bridge.
- Make shortcut rows editable from the Vue settings panel.
- Capture keyboard combinations into the existing visual format.
- Detect duplicate shortcut assignments before saving.
- Make settings close/back controls actually close the panel.

## Capabilities

### Modified Capabilities

- `overlay-settings`: settings become persisted and editable from the overlay.
- `overlay-launcher-desktop-ui`: the settings panel changes from static mock UI to functional controls.

## Impact

- Affects `desktop/electron/`, `desktop/src/`, and desktop tests.
- Stores desktop UI settings in Electron user data as JSON.
- Does not yet re-register the separate Python Windows shortcut listener at runtime; that integration remains a follow-up once the listener consumes the shared settings file or gets a reload mechanism.
