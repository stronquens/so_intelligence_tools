# Validation

## Summary

Implemented push-to-talk dictation with an ONNX CPU Nemotron adapter, microphone capture through `parec`, a press-and-hold keyboard listener, incremental final-segment insertion, CLI commands, persistent `systemd --user` service installation, documentation and tests.

Update 2026-06-13: user testing shows the feature is not ready to archive as complete. The atajo and runtime respond, but text insertion quality is still unreliable.

## Evidence

- Runtime spike: `research/runtime-spike.md`
- ONNX CPU preflight command:

```text
$ poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
Push-to-talk dictation runtime ready
```

- Automated tests:

```text
$ poetry run pytest -q
101 passed, 1 warning in 3.74s
```

- Product lint scope:

```text
$ poetry run ruff check src tests scripts
All checks passed!
```

- Post-install bugfix:
  - Observed repeated press/release events of a few milliseconds in `journalctl --user -u so-intelligence-tools-push-to-talk-dictation.service`.
  - Verified microphone capture independently with `parec`; 2.66 s of PCM had non-zero RMS/peak.
  - Verified ONNX ASR transcribed that captured PCM.
  - Added key-release debounce to ignore keyboard autorepeat release/press churn.
  - Switched dictation insertion to direct keyboard typing first, with clipboard paste as fallback.
  - Restarted the user service; status returned `active`.

- Poetry validation:

```text
$ poetry check
Command succeeded. It reports existing Poetry metadata deprecation warnings.
```

- Persistent service install on this machine:

```text
$ poetry run so-intelligence-tools install-push-to-talk-dictation-service
Push-to-talk dictation service installed: /home/sciling/.config/systemd/user/so-intelligence-tools-push-to-talk-dictation.service
Push-to-talk dictation service state: enabled and started now

$ systemctl --user is-active so-intelligence-tools-push-to-talk-dictation.service
active

$ systemctl --user is-enabled so-intelligence-tools-push-to-talk-dictation.service
enabled
```

## Requirement Mapping

- Streaming local ASR runtime:
  - Implemented `StreamingAsrTranscriber` and `StreamingAsrSession` port in `src/so_intelligence_tools/ports/streaming_asr.py`.
  - Implemented ONNX CPU Nemotron adapter in `src/so_intelligence_tools/push_to_talk_dictation/onnx_cpu.py`.
  - Verified runtime with `check-push-to-talk-dictation-runtime`.

- Press-and-hold dictation:
  - Implemented `PressAndHoldShortcutListener` for key-down/key-up handling.
  - Implemented `PressAndHoldDictationRunner` that starts capture on press and stops capture before ASR finalization on release.
  - Covered by `tests/test_press_and_hold_listener.py` and `tests/test_push_to_talk_dictation_session.py`.

- Literal natural-language insertion:
  - Controller inserts ASR `final` events directly without spoken formatting-command mapping.
  - Partial events are logged/ignored for external text insertion.
  - Covered by fake ASR tests.

- Stable/final segment tracking:
  - Controller inserts final segments incrementally.
  - It handles cumulative final hypotheses by inserting only the delta.
  - Covered by `test_streaming_dictation_tracks_stable_delta_for_cumulative_finals`.

- Desktop persistence:
  - Added `so-intelligence-tools-push-to-talk-dictation.service`.
  - Integrated service installation into `install-linux-desktop-integration`.
  - Extended `scripts/ensure-linux-desktop-integration.sh` to reinstall/start the dictation service after login.
  - Covered by `test_install_push_to_talk_dictation_service_writes_unit`.

- User-visible state:
  - Controller sends notifications for start, completion and ASR errors.
  - This satisfies the first implementation's "overlay or notification" state requirement.

## Residual Risk

- User-reported pending issue on 2026-06-13:
  - When holding the shortcut and starting to speak, transcription starts a couple of seconds late and initial words can be lost.
  - The text inserted into the focused field can appear out of order.
  - Sometimes already inserted text is erased/replaced and then dictation continues.
  - This points to the insertion/stabilization layer, not to the keyboard shortcut itself.
- The press-and-hold listener is X11-first. GNOME Wayland is explicitly rejected for this listener until a Wayland-specific backend is added.
- The ONNX CPU model is fast enough on this machine in the recorded spike, but other CPUs may need a runtime-too-slow diagnostic threshold.
- Live insertion depends on existing Linux clipboard/keyboard automation. When direct paste fails, the existing adapter path has already placed text on the clipboard before keyboard automation, but user-facing fallback UX can still be improved.

## Follow-up Needed

- Add audio pre-roll or warm model/session before accepting speech so initial words are not lost.
- Stop inserting token-sized fragments directly into external fields; use a session buffer and append only confirmed stable blocks.
- Add integration tests for out-of-order ASR emissions and destructive insertion regressions.
- Capture a real debug trace with audio chunk timings, first-token latency, ASR emitted text and actual inserted text.
