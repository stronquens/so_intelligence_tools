## 1. Safer Configuration

- [x] 1.1 Lower voice translation defaults and example values to safe levels.
- [x] 1.2 Update the local `.env` volume values for the next live test.
- [x] 1.3 Add a configurable safety cap for ducked passthrough.

## 2. Audio Safeguards

- [x] 2.1 Add PCM limiter helper and apply it to translated output.
- [x] 2.2 Reject monitor or project-virtual sources as physical microphone inputs.
- [x] 2.3 Log requested vs applied ducking values during translation.

## 3. Validation

- [x] 3.1 Add unit tests for safe defaults, ducking cap, limiter, and source validation.
- [x] 3.2 Run targeted/full tests and record validation evidence in the change.
