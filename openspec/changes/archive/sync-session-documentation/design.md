# Design

This change keeps the implementation untouched and aligns documentation with the already-validated runtime state.

## Documentation Targets

- `README.md`: public overview, Windows quick start, roadmap and limitations.
- `AGENTS.md`: project-level operating context for future agents.
- `docs/README.md`: documentation index status.
- `docs/architecture.md`: current architecture and Windows adapter capabilities.
- `docs/windows-support.md`: overlay shortcut plus current Windows support.
- `docs/desktop-ui.md`: current Electron overlay/settings bridge state.

## Validation

Validation should confirm that the changed docs consistently mention:

- `Ctrl + Alt + A` opens/toggles the main overlay on Windows.
- `Ctrl + Alt + D` is the Windows push-to-talk dictation shortcut.
- faster-whisper HTTP via Docker is the preferred validated Windows dictation backend.
- Linux remains the most complete audio-routing target, while Windows has useful text/overlay/dictation workflows.
