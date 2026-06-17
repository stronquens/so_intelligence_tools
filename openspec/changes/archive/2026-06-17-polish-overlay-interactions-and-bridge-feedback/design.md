## Interaction Motion

Use CSS transitions and keyframes only. No new runtime dependency is needed.

Targets:

- launcher/settings panel entrance
- tool card hover and press
- icon glow and scale
- settings row hover
- save button hover and press
- toggle animation

## Bridge Feedback

The renderer should not ask for `desktopBridge` before it knows the selected tool requires Electron command dispatch. Current wired tools:

- `selected-text-correction`: requires `desktopBridge`
- `system-audio-translation`: requires `desktopBridge` and opens or focuses the local Vue translator view in a separate Electron window

All other tools remain visible but should return pending feedback.
