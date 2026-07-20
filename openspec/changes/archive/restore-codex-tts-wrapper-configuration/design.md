## Context

The Linux Codex voice path is event-driven: VS Code launches `scripts/codex-tts-wrapper.py`, the wrapper proxies the bundled Codex app-server and forwards visible lifecycle events to the TTS listener, and the listener sends speech to Piper. Piper and the voice-runtime user service are healthy, but VS Code currently launches the bundled Codex binary directly because `chatgpt.cliExecutable` was removed after a transient `ENOENT` spawn failure on 2026-07-16.

## Goals / Non-Goals

**Goals:**

- Restore the existing wrapper as the executable selected by the VS Code Codex extension.
- Preserve every unrelated VS Code user setting.
- Verify compatibility with the currently installed extension and bundled Codex CLI.
- Confirm that a newly loaded Codex process creates an active wrapper voice session.

**Non-Goals:**

- Replace Piper, change voice presets, or modify event filtering.
- Add a permanent background session monitor on Linux.
- Change the Codex extension or bundled CLI.

## Decisions

- Edit the existing JSON user settings file in place and add only `chatgpt.cliExecutable`. This restores the documented integration boundary without changing project code.
- Keep the wrapper path absolute because the extension launches outside a repository-relative working directory.
- Reload VS Code after writing the setting because existing app-server processes retain the executable chosen at process creation.
- Validate both static configuration and runtime behavior: wrapper CLI resolution, focused tests, Piper readiness, and active voice-session registration after reload.

## Risks / Trade-offs

- [The extension marks `chatgpt.cliExecutable` as development-only] → Keep the change limited to the known working wrapper and verify against the installed extension version.
- [Reloading VS Code interrupts active Codex turns] → Perform the reload after saving configuration and report that the current turn may finish before the new wrapper becomes active.
- [A future extension update may remove or reset the setting] → Preserve the diagnostic evidence and retain the documented one-line recovery procedure.
- [The prior `ENOENT` failure could recur] → Confirm the wrapper path, executable bit, shebang, and current direct execution before reloading.
