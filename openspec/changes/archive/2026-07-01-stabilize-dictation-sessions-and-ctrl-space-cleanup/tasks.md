## 1. Implementation

- [x] 1.1 Serialize dictation runner press/release operations to prevent overlapping sessions.
- [x] 1.2 Add regression tests for pressing again while release/final transcription is still running.
- [x] 1.3 Expand and preserve best-effort Linux `Ctrl + Space` cleanup tests, including Ulauncher.

## 2. Documentation

- [x] 2.1 Document warm runtime semantics and buffered-on-release latency.
- [x] 2.2 Document that OS-level `Ctrl + Space` bars require service restart/new shortcut or desktop binding cleanup, not a reliable `preventDefault`.

## 3. Validation

- [x] 3.1 Run focused dictation/session and user service tests.
- [x] 3.2 Record validation results and residual risk in this change.
