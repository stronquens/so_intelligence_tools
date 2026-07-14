## Why

Long-running OpenAI Realtime translation sessions can keep showing current speech while failing to promote completed turns into the accumulated history. Production logs show that one turn without an original transcript can block later complete turns for several minutes, and reconnecting or stopping can discard the pending visible content.

## What Changes

- Make realtime turn publication independent so one incomplete turn cannot block later complete turns.
- Finalize incomplete turns with the best available original and translation when a response ends, the connection reconnects, or the session stops.
- Deduplicate provider events by stable turn/response identity instead of translated text content.
- Preserve pending turn state through controlled connection teardown and expose explicit logging for incomplete turns and dropped audio.
- Add regression coverage based on the event ordering observed in real session logs.
- Keep the Electron translator bridge and visual redesign out of scope; this change stabilizes the existing functional Python backend first.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `system-audio-transcription`: realtime translation SHALL publish completed turns without head-of-line blocking and SHALL finalize or explicitly account for pending visible content during stop and reconnect.

## Impact

- `src/so_intelligence_tools/system_audio_translation/openai_realtime.py`
- Realtime session lifecycle and logging behavior
- `tests/test_system_audio_translation_realtime.py`
- System audio translation documentation
- No new runtime dependency or public CLI command
