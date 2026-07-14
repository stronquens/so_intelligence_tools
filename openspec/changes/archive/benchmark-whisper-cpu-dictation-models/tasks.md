## 1. Benchmark Setup

- [x] 1.1 Add an isolated benchmark script under the change directory.
- [x] 1.2 Select candidate CPU models and sample audio inputs.
- [x] 1.3 Ensure temporary Docker containers and volumes are cleaned up.

## 2. Benchmark Execution

- [x] 2.1 Run the current `large-v3-turbo` baseline.
- [x] 2.2 Run medium/small-family candidates where supported.
- [x] 2.3 Save raw JSON and a concise markdown summary.

## 3. Validation

- [x] 3.1 Verify the production `whisper-server` remains running on the original model.
- [x] 3.2 Verify temporary benchmark containers and volumes are removed.
- [x] 3.3 Record findings, caveats, and recommendation in `validation.md`.
