## Why

The Codex voice bridge currently speaks confusing lifecycle cues in the VS Code extension: task start may be announced twice and "Fin de tarea" can be spoken before the assistant has actually finished, for example around the first tool call.

This makes the Piper integration feel unreliable even when TTS itself is healthy.

## What Changes

- Treat only true Codex turn completion events as task-end boundaries.
- Deduplicate repeated turn-start announcements from equivalent app-server/JSONL events.
- Add regression tests for VS Code-style event sequences where tool calls happen inside an active turn.
- Keep the existing speech detail modes, voices, Docker service and Piper API unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `local-tts-voice-output`: Codex voice-output lifecycle boundaries must not duplicate task start or announce task end for intermediate tool events.

## Impact

- `src/so_intelligence_tools/local_tts/codex_events.py`
- `src/so_intelligence_tools/local_tts/codex_voice.py`
- `tests/test_codex_voice_events.py`
- `docs/piper-tts-voice-output.md`
