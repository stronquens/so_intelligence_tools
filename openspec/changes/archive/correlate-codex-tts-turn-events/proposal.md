## Why

The Codex voice listener can announce “Fin de tarea” immediately after “Inicio de tarea” because it treats lifecycle events from all app-server threads as one global turn. Codex now supplies `threadId` and `turnId` on lifecycle events, so the bridge must correlate them instead of relying on message-order heuristics.

## What Changes

- Track the active Codex lifecycle by its protocol `threadId` and `turnId`.
- Ignore completion, message, and action events that identify a different turn while a spoken turn is active.
- Deduplicate terminal notifications for an already completed correlated turn.
- Determine successful, failed, and interrupted completion from the terminal turn status.
- Retain conservative fallback behavior for legacy event shapes that do not contain identifiers.
- Add regression coverage for interleaved turns, duplicate completions, and legacy streams.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `local-tts-voice-output`: Task boundary speech must correlate start, progress, and completion events to the same Codex thread and turn before announcing completion or clearing queued speech.

## Impact

- `src/so_intelligence_tools/local_tts/codex_events.py` turn-state extraction.
- `src/so_intelligence_tools/local_tts/codex_voice.py` completion queue handling.
- Focused Codex voice event and playback tests.
- No changes to Piper, voices, Docker services, or public CLI commands.
