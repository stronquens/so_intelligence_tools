# Document global `so-ai` command

## Summary

Document the persistent `so-ai` command used to control local voice/TTS tooling from any VS Code project window.

## Motivation

Per-window Codex voice controls are often run from terminals opened in projects other than `so_intelligence_tools`. In those windows, `poetry run so-intelligence-tools ...` is not available because Poetry resolves the current project. A persistent command in `~/.local/bin/so-ai` avoids that confusion.

## Scope

- Document the `~/.local/bin/so-ai` symlink pattern.
- Clarify that `listen-codex-visible-events` is an internal stdin listener, not the command for changing an active window setting.
- Show per-window examples for `minimal`, `actions`, and `female` voice.
