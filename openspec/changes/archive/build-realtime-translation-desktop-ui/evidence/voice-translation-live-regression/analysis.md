# Live voice-translation regression — 2026-07-14

## Source evidence

User-triggered functional session:

`~/.cache/so_intelligence_tools/voice_translation_logs/system-audio-session-20260714-132458.log`

No additional paid provider session was started during diagnosis or validation.

## Findings

- The session connected to `gpt-realtime-translate` with Spanish input and
  English output at 13:24:04.
- The provider emitted translated transcript deltas in English and the pipeline
  wrote 1,920,000 translated-audio bytes to `so_ai_translated_mic`. This proves
  that the translation endpoint, target-language payload and virtual output
  route were active during the reported failure.
- `OpenAIRealtimeVoiceTranslationController._set_state()` also printed Spanish
  status text to process `stdout`. The Electron child parser reserves that
  stream for JSONL, which reproduces the visible `Unexpected token 'T'` error.
- Stop was requested at 13:24:44. The controller published an inactive state
  four seconds later, but its receiver timed out and audio processing continued
  afterward. The UI state therefore preceded actual worker termination.

## Corrections

- Voice status diagnostics now use `stderr`; a regression asserts empty stdout.
- Electron logs and discards isolated non-JSON stdout instead of publishing a
  fatal UI error.
- The duplicated active callback was removed.
- Realtime close drain keeps its eight-second allowance for final translated
  output, websocket close is bounded to one additional second,
  and the controller waits for its worker before publishing inactive. A stuck
  worker produces an error state instead of a false inactive state.

## Provider-free validation

- `poetry run pytest -q tests/test_voice_translation_realtime.py tests/test_voice_translation_pipeline.py tests/test_system_audio_translation_app.py`
  — 19 passed.
- `cd desktop && npm test -- --run` — 26 passed.
- `cd desktop && npm run build` — Vite and Electron TypeScript build passed.

The official Realtime translation guide confirms the implemented architecture:
dedicated translation WebSocket, `session.audio.output.language`, continuous
24 kHz PCM16 append events, output audio/transcript deltas and `session.close`
followed by a drain until `session.closed`.

Official reference: https://developers.openai.com/api/docs/guides/realtime-translation
