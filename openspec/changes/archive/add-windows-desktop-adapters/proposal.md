# Proposal

## Summary

Add an initial Windows desktop adapter layer so text-focused tools can run on Windows without rewriting the application use cases.

This first iteration targets the selected text correction path and the shared runtime factory. It keeps Linux behavior intact while adding Windows implementations for clipboard, keyboard copy/paste automation, text selection, text insertion and basic notifications.

## Why

The project is Linux-first today, but its architecture already separates product logic from operating-system integration through ports and adapters. Windows support should start by proving that boundary with the smallest useful tool path instead of jumping directly into audio routing or virtual microphone support.

Selected text correction is the best first Windows slice because it exercises:

- selected text discovery
- clipboard preservation
- keyboard copy/paste automation
- insertion into the focused app
- clear fallback behavior when the focused app cannot be automated

## Scope

### In scope

- Create `adapters/windows/` for text-oriented desktop adapters.
- Add a platform-aware runtime factory that can build Linux or Windows runtimes.
- Update the selected text correction CLI path to use the platform-aware runtime.
- Keep Linux-specific installation and GNOME shortcut commands unchanged.
- Add focused unit tests for runtime selection and Windows adapter behavior that can run without touching the real desktop.
- Document current Windows limitations.

### Out of scope

- Windows global shortcut installation.
- Windows startup/service installation.
- Screenshot region capture on Windows.
- Push-to-talk dictation microphone capture on Windows.
- System audio loopback capture on Windows.
- Translated virtual microphone support on Windows.

## Expected Outcome

The repository should have a clear first Windows adapter path for text tools:

- application use cases stay reusable
- Windows adapters live beside Linux adapters
- runtime selection is centralized
- unsupported Windows features fail explicitly rather than pretending to work

## Risks

- Windows desktop automation can be blocked by focus, permissions, UAC boundaries or apps that intercept clipboard shortcuts.
- Clipboard roundtrips can disturb the user's clipboard if restoration fails.
- Keyboard simulation through Win32 APIs is less expressive than a full accessibility/UI automation layer.

## Mitigations

- Keep the first implementation narrow and testable.
- Preserve and restore the clipboard during selected-text probing.
- Use the existing fallback clipboard behavior when direct replacement fails.
- Leave audio and persistent desktop integration for later changes with their own design.
