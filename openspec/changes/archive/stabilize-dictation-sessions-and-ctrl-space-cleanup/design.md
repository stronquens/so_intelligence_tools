## Context

The faster-whisper HTTP backend is kept warm by Docker Compose and checked through `/v1/models` before the listener starts. However, the actual dictation session stores PCM chunks and sends one transcription request in `finish()`, after the shortcut is released.

The press-and-hold listener marks the shortcut inactive before calling the runner's release handler. That lets a fast follow-up press call `runner.press()` while the previous `runner.release()` is still waiting on post-roll, HTTP transcription, or text insertion. The shared controller/result state can then be reset by the new session before the old finish path inserts text.

## Goals / Non-Goals

**Goals:**

- Prevent overlapping dictation sessions in one runner.
- Preserve the current warm faster-whisper HTTP backend setup.
- Keep cleanup of old `Ctrl + Space` OS/app bindings best-effort and non-fatal.

**Non-Goals:**

- Implement true streaming ASR for faster-whisper HTTP.
- Globally suppress keyboard events at the OS level.
- Change the new `Ctrl + Shift + Space` default.

## Decisions

- Add a non-blocking runner operation lock for `press()`. If release/finalization is still busy, a new press is ignored instead of starting a second capture.
- Let `release()` hold the same lock through post-roll, capture stop, final transcription, and insertion. This keeps the controller/result lifecycle single-session.
- Keep model warm-up as readiness checks plus the long-lived Docker service. This reduces cold-start cost, but the transcription latency remains tied to utterance length and model speed.
- Do not rely on a `preventDefault` equivalent. `pynput` observes global key events and does not provide safe per-shortcut event cancellation for GNOME search or shell shortcuts.
- Clear Ulauncher `hotkey-show-app` when it is set to `<Primary>space`, because on the current machine Ulauncher is the component opening the visible search bar.

## Risks / Trade-offs

- A press made while the previous dictation is finalizing is dropped. This is preferable to mixing audio/text across sessions.
- If the user still sees `Ctrl + Space`, the running listener may still be old or another launcher may own that key. Restarting or disabling that launcher may be required after config cleanup.
