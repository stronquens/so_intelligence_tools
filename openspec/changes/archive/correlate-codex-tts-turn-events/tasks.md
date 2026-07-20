## 1. Correlate lifecycle events

- [x] 1.1 Extract normalized thread and turn identifiers from modern and legacy Codex event shapes.
- [x] 1.2 Track the active correlated turn and ignore identified events belonging to another turn.
- [x] 1.3 Deduplicate correlated terminal events and derive completion speech from terminal status.

## 2. Protect playback semantics

- [x] 2.1 Ensure unrelated completion events do not flush active text or clear queued speech.
- [x] 2.2 Preserve conservative identifier-less event behavior for legacy integrations.

## 3. Validate

- [x] 3.1 Add regression tests for interleaved turns, duplicate completions, background progress, and legacy events.
- [x] 3.2 Run focused and full test suites, strict OpenSpec validation, and record evidence in `validation.md`.
- [x] 3.3 Restart active VS Code Codex wrapper processes so the validated listener code is loaded.
