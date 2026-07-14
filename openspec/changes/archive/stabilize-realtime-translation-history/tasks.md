## 1. Realtime Turn Lifecycle

- [x] 1.1 Introduce connection turn state that can publish independently complete turns.
- [x] 1.2 Finalize complete, translation-only, and original-only residual turns on normal exit or cancellation.
- [x] 1.3 Replace translated-text deduplication with provider turn identity.

## 2. Connection And Buffer Observability

- [x] 2.1 Ensure receiver cancellation finalizes pending turn state before it propagates.
- [x] 2.2 Record cumulative audio chunk drops when the bounded realtime queue overflows.

## 3. Regression Coverage

- [x] 3.1 Add a live-stream regression for an incomplete first turn followed by a complete later turn.
- [x] 3.2 Add regressions for receiver cancellation and translation-only residual finalization.
- [x] 3.3 Add regressions for identical consecutive translations and audio queue overflow logging.

## 4. Validation And Documentation

- [x] 4.1 Run focused realtime translation tests and the full Python test suite.
- [x] 4.2 Run Ruff and OpenSpec validation.
- [x] 4.3 Record validation results and residual risks in `validation.md`.
