## Why

CPU-only dictation currently uses `large-v3-turbo`, which preserves Spanish quality but feels slow because transcription happens after release. We need measured latency and quality evidence before changing the default model.

## What Changes

- Run an isolated benchmark comparing the current model with smaller/faster Whisper candidates on CPU.
- Capture latency, realtime factor, transcript output, and quality deltas against a reference transcript or a large-model pseudo-reference.
- Ensure benchmark containers use temporary ports and temporary Docker volumes, then remove them so the current `whisper-server` and retained model cache remain unchanged.
- Preserve only benchmark scripts/results inside this change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `push-to-talk-dictation`: model selection should be supported by measured CPU latency and Spanish quality evidence before changing defaults.

## Impact

- Benchmark-only scripts and result artifacts under this OpenSpec change.
- No product runtime change unless the benchmark identifies a better default and a later change applies it.
