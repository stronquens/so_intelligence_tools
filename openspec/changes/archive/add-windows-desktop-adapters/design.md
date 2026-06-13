## Context

The current runner architecture already has ports for text selection, text insertion, clipboard, screenshot and notifications. Linux implementations are assembled by `build_linux_runtime()`, while the selected-text correction use case only depends on the port-shaped runtime object.

Windows support should preserve that structure. The implementation should not move product logic into the CLI or into platform adapters.

## Goals / Non-Goals

**Goals**

- introduce Windows adapters for the text correction path
- centralize platform selection in a runtime factory
- keep Linux runtime behavior stable
- make unsupported Windows capabilities explicit
- validate through unit tests that do not require active desktop automation

**Non-Goals**

- complete Windows parity for every feature
- audio loopback capture or virtual microphone support
- permanent Windows shortcut registration
- a full UI Automation abstraction

## Decisions

Add a shared runtime protocol and a `build_runtime()` factory.
Reason: selected-text correction and shortcut actions only need a small set of attributes. A protocol lets Linux and Windows runtimes be interchangeable without forcing inheritance.

Keep `build_linux_runtime()` as a public function.
Reason: existing Linux-only modules such as push-to-talk dictation and GNOME shortcut listener still depend on it directly.

Use `ctypes` for the first Windows clipboard and keyboard implementation.
Reason: the repo does not currently depend on `pywin32`, and the first slice can be implemented with standard-library access to Win32 APIs.

Implement Windows text selection by clipboard roundtrip.
Reason: it matches the existing Linux fallback behavior and works across many applications using `Ctrl+C`, while preserving the previous clipboard when possible.

Implement Windows text insertion by setting the clipboard and sending `Ctrl+V`.
Reason: this is the most reliable cross-application primitive for the first pass.

Treat Windows notifications as best-effort.
Reason: native toast notifications require extra packaging or dependencies. For this change, notification failure should not break the tool flow.

## Proposed Architecture

```text
src/so_intelligence_tools/
  adapters/
    linux/
    windows/
      clipboard.py
      keyboard.py
      notification.py
      text_insertion.py
      text_selection.py
  infrastructure/
    runtime.py
```

`runtime.py` should expose:

- `ToolRuntime` protocol
- `LinuxRuntime`
- `WindowsRuntime`
- `build_linux_runtime()`
- `build_windows_runtime()`
- `build_runtime()`

`build_runtime()` should default to auto-detection using `sys.platform`, while allowing tests or future callers to pass an explicit platform name.

## Validation Strategy

- Unit-test platform selection.
- Unit-test Windows text selection/insertion using fake clipboard and keyboard adapters.
- Unit-test Windows clipboard platform guard behavior without requiring real clipboard access.
- Run the relevant pytest subset for text adapters and runtime.
- Run ruff on touched source and tests.

## Open Questions

Windows shortcut installation should be designed separately. Candidate paths include a small resident listener, Task Scheduler startup registration, or Electron-level global shortcut handling.

Windows audio support should be designed separately. Candidate paths include WASAPI loopback for system audio, `sounddevice`/PortAudio for microphone capture, and a third-party virtual audio cable or driver-backed strategy for translated microphone output.
