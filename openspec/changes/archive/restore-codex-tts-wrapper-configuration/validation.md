## Summary

The VS Code Codex TTS bridge configuration was restored and validated against the installed Codex extension and Piper runtime. A real VS Code window reload produced a new active wrapper-managed voice session, confirming that the extension adopted `chatgpt.cliExecutable`.

## Validation approach

- Parsed the modified VS Code user settings as JSON and confirmed the absolute wrapper setting.
- Executed the wrapper directly and confirmed it resolved `codex-cli 0.145.0-alpha.18`.
- Confirmed Piper reported `ready` and submitted an audible speech smoke phrase successfully.
- Ran 36 focused wrapper, event, control, and TTS client tests.
- Started an isolated wrapper app-server and observed its registered voice session.
- Reloaded an existing VS Code window and observed a newly registered wrapper voice session.
- Ran strict OpenSpec validation.

## Requirement mapping

### VS Code Codex voice bridge activation

- **Voice bridge is enabled:** `chatgpt.cliExecutable` points to the executable repository wrapper; PID 174840 appeared as an active `actions` voice session after a VS Code reload.
- **Existing VS Code process predates the setting:** an existing window was reloaded and its replacement Codex process registered through the wrapper.
- **Wrapper cannot be launched:** executable mode, direct CLI resolution, focused failure-path tests, and Piper readiness were checked independently so backend health was not used as the sole success signal.

## Evidence

- [Runtime checks](evidence/runtime-check.txt)

## Residual risk

The extension labels `chatgpt.cliExecutable` as development-only, so a future extension or settings-sync operation could remove it again. The repository documentation and this evidence retain the recovery path. Each VS Code window that was already open before the setting changed must reload once; newly opened windows adopt it automatically.
