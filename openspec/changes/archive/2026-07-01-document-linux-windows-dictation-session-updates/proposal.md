## Why

Recent dictation work changed Linux behavior materially: the default shortcut is now `Ctrl + Shift + Space`, the Linux installer starts the warm faster-whisper Docker backend, old `Ctrl + Space` desktop conflicts are cleaned up best-effort, and CPU model benchmarking kept `large-v3-turbo` as the Linux default. The public docs should preserve that state clearly without mixing it up with the separately validated Windows workflow.

## What Changes

- Update Linux-facing documentation to describe the current push-to-talk dictation setup, shortcut, Docker runtime, latency model, and troubleshooting notes.
- Keep Windows documentation separate where validation status or startup mechanisms differ.
- Link the Linux CPU benchmark and Nemotron backup docs from the appropriate Linux/dictation pages.
- Keep README and docs index status language aligned with the current platform split.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-documentation`: feature docs must distinguish Linux and Windows status, commands, shortcuts, and validation state when they differ.

## Impact

- Documentation-only change.
- No runtime, Docker, service, shortcut, API, or dependency changes.
