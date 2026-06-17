## Why

The launcher overlay now looks like the intended product surface, but the tool cards are still visual-only. The next step is to make the overlay a real operating surface that dispatches application commands through Electron and starts by wiring the existing selected-text correction tool.

## What Changes

- Add a typed desktop command bridge between Vue and Electron.
- Make overlay tool cards clickable and observable instead of visual-only.
- Wire the `Corregir texto` card to the existing selected-text correction runner.
- Hide the overlay before running OS automation so the previously focused application can receive copy/paste actions.
- Add user feedback for running, success, failure, and not-yet-implemented tools.
- Keep the remaining tool cards visible but return explicit pending feedback until their capabilities are wired in later changes.

## Capabilities

### New Capabilities

- `overlay-action-dispatch`: Electron/Vue command dispatch from overlay tool cards to local application actions.

### Modified Capabilities

- `overlay-launcher-desktop-ui`: tool cards change from visual-only controls to command-dispatching controls with user-visible status feedback.
- `selected-text-correction`: selected-text correction can be invoked from the overlay in addition to the existing shortcut/CLI path.

## Impact

- Affects `desktop/electron/`, `desktop/src/`, and desktop tests.
- Uses the existing Poetry CLI runner for selected text correction.
- Does not implement OCR, dictation, audio translation, assistant, summary, or capture workflows yet.
- Does not replace the existing global shortcut listener.
