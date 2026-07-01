## Why

The project has migrated push-to-talk dictation toward faster-whisper HTTP, but the previous Linux Nemotron ONNX CPU prototype was useful context and should remain recoverable. The current repository no longer has the old Nemotron implementation or its active OpenSpec change in the live tree.

## What Changes

- Add English Linux backend documentation for the current Whisper route and the previous Nemotron ONNX CPU dictation prototype.
- Link those guides from the push-to-talk dictation documentation and docs index.
- Document the source commit and files that can be inspected or restored if Nemotron streaming dictation is needed again.

## Capabilities

### New Capabilities

- `dictation-runtime-backup-documentation`: Documentation preserves how to choose, inspect, and recover dictation runtimes without making retired runtimes the default path.

### Modified Capabilities

None.

## Impact

- Documentation and OpenSpec artifacts only.
- No runtime behavior changes.
- Whisper/faster-whisper remains the current recommended dictation runtime.
