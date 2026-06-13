## 1. Runtime And Configuration

- [x] 1.1 Add settings for streaming dictation model, language, microphone source, chunk size, insertion strategy and `Ctrl+Alt+Space` shortcut.
- [x] 1.2 Define `StreamingAsrTranscriber` port and event models for partial/final/error/state updates.
- [x] 1.3 Run and document a runtime spike comparing Ollama support vs Docker/NVIDIA NIM/NeMo and ONNX CPU for Nemotron ASR.
- [x] 1.4 Add a Nemotron 3.5 ASR adapter skeleton behind the port for the selected local runtime path, with dependency checks.

## 2. Dictation Flow

- [x] 2.1 Implement microphone capture for push-to-talk streaming sessions.
- [x] 2.2 Implement session controller that starts on key down, streams audio only while held, stops capture on key up, and finalizes the ASR stream.
- [ ] 2.3 Implement stable segment tracking to insert final text incrementally without duplication.
- [x] 2.4 Keep dictated content literal, with no spoken formatting-command mapping in this phase.

## 3. Desktop Integration

- [x] 3.1 Register a GNOME/global shortcut for streaming dictation with diagnostic wrapper logs.
- [x] 3.2 Integrate streaming dictation into `install-linux-desktop-integration` so it persists after reboot/login.
- [x] 3.3 Add or extend user-level service/autostart healthcheck to keep the shortcut/runtime integration available.
- [x] 3.4 Add overlay or notification states for listening, transcribing, inserting and errors.
- [x] 3.5 Implement fallback behavior when focused text insertion is unavailable.

## 4. Validation

- [ ] 4.1 Add unit tests with fake streaming ASR events for partial/final insertion behavior.
- [x] 4.2 Add tests that natural-language dictation is inserted literally.
- [x] 4.3 Validate that key-up stops capture/transcription.
- [ ] 4.4 Validate reboot/login persistence path or record equivalent service/shortcut evidence in `validation.md`.

## 5. Pending Stabilization From User Testing

- [ ] 5.1 Add pre-roll or runtime warm-up so the first spoken words are not lost after key-down.
- [ ] 5.2 Replace token-by-token external insertion with a non-destructive session buffer and append-only stable block commits.
- [ ] 5.3 Add tests for out-of-order, cumulative and replacement-style ASR emissions so text is never duplicated, reordered or erased unexpectedly.
- [ ] 5.4 Capture a real debug trace with audio timing, first-token latency, ASR emissions and inserted text before re-validating.
