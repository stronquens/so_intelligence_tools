# Tasks

- [x] Refine the system-audio-transcription spec for toggle-by-shortcut behavior
- [x] Add keyboard-shortcuts delta behavior for same-shortcut open/close toggling
- [x] Define the first iteration target as English audio translated to Spanish
- [x] Define pause, resume, reset, and close behavior from the window
- [x] Define the Linux-first audio capture strategy and adapter boundary
- [x] Define the session controller states and failure handling
- [x] Define bounded buffering expectations for temporary reconnect-and-catch-up
- [x] Run a provider/model spike for remote live translation quality versus latency
- [x] Decide an initial low-conflict default shortcut for Linux while keeping it configurable later
- [x] Prepare implementation validation criteria for start, stop, and repeated toggle cycles
- [x] Choose the Phase 1 Python UI toolkit for the dedicated window
- [x] Validate Linux monitor-source capture with real system speaker output on the target machine
- [x] Compare a direct realtime translation path against an ASR-plus-translation path
- [x] Lock the initial chunk size, sample rate, and buffering approach for the first implementation
- [x] Expose a visible mode dropdown in the first window iteration and wire it to switch between `OpenAI realtime` and `chunked` fallback pipelines
- [x] Tune OpenAI realtime VAD sensitivity for shorter pauses while keeping readable grouped blocks
- [x] Add richer session logs for state changes, partial updates, final transcriptions, final translations, and published blocks
