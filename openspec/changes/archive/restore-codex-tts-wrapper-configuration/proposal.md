## Why

Codex voice output stopped because VS Code no longer routes the Codex app-server through the repository's TTS wrapper. The local Piper runtime remains healthy, so the missing integration setting must be restored and verified against the currently installed Codex extension.

## What Changes

- Restore the VS Code user-level `chatgpt.cliExecutable` setting so Codex launches through `scripts/codex-tts-wrapper.py`.
- Reload the active VS Code window so the extension adopts the restored executable.
- Verify the wrapper resolves the current bundled Codex CLI, registers a voice session, and can send task-boundary speech to Piper.
- Record durable diagnostic and validation evidence in this change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `local-tts-voice-output`: Clarify the operational requirement that the VS Code Codex extension must launch through the configured TTS wrapper for task-boundary speech to function.

## Impact

- User-level VS Code configuration at `~/.config/Code/User/settings.json`.
- The running VS Code/Codex extension process, which must be reloaded.
- Existing wrapper, listener, Piper service, tests, and operational documentation; no new dependency or API is introduced.
