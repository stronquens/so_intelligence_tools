# Proposal

## Summary

Add an initial Windows global shortcut path for selected text correction.

The previous Windows adapter slice made the tool runnable from the CLI. This change adds a resident Windows shortcut listener and a user-level Startup installer so `Ctrl+Alt+C` can trigger selected text correction from any focused application after login.

## Why

The product is meant to feel native through system shortcuts, not only manual commands. Windows text adapters are useful, but they need a running listener to become a day-to-day tool.

## Scope

### In scope

- Add a Windows shortcut listener using the existing `pynput` dependency.
- Make `listen-shortcuts` compose the platform-aware runtime and listener.
- Add a Windows default selected-text shortcut setting.
- Add a user-level Windows Startup installer for the shortcut listener.
- Document how to run and install the Windows shortcut listener.
- Add focused tests for listener selection and Startup script generation.

### Out of scope

- Windows shortcut capture for press-and-hold dictation.
- Electron `globalShortcut` integration.
- Windows Task Scheduler integration.
- Admin-level service installation.
- Audio, screenshot and virtual microphone shortcuts on Windows.

## Expected Outcome

The user can install a Windows startup entry and use `Ctrl+Alt+C` to trigger selected text correction once the listener is running.

## Risks

- `pynput` global hotkeys may be blocked by some security contexts or elevated applications.
- A resident listener must remain running for shortcuts to work.
- The listener startup entry can only start after login; it is not a Windows service.

## Mitigations

- Keep the listener user-level and easy to inspect.
- Generate a simple Startup `.cmd` file in the user's Startup folder.
- Keep existing manual CLI execution path as fallback.
