## 1. PulseAudio Device Model

- [x] 1.1 Update virtual microphone creation to load an internal null sink and a remapped input source.
- [x] 1.2 Ensure passthrough and translated audio write to the internal sink while user-facing state exposes the virtual source name.
- [x] 1.3 Clean up both PulseAudio modules on stop, including partial-failure cleanup.

## 2. User-Facing Contract

- [x] 2.1 Update runtime messages and logs to tell users to select `so_ai_translated_mic` as microphone.
- [x] 2.2 Update README and Linux installation docs to stop instructing users to select `.monitor`.

## 3. Validation

- [x] 3.1 Update unit tests for module loading, sink/source names, and cleanup.
- [x] 3.2 Run targeted tests and record validation evidence in the change.
