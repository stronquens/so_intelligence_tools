# Validation

## Summary

Validated safer voice translation audio levels, ducking cap behavior, PCM limiting, and rejection of unsafe capture sources. The local `.env` now uses the safe test values requested for the next live Slack run.

## Automated

- `poetry run pytest tests/test_voice_translation_virtual_microphone_audio.py tests/test_voice_translation_pipeline.py tests/test_voice_translation_realtime.py tests/test_system_audio_translation_app.py -q`
  - Result: `25 passed in 0.39s`
- `poetry run ruff check src/so_intelligence_tools/voice_translation_virtual_microphone src/so_intelligence_tools/infrastructure/config.py tests/test_voice_translation_virtual_microphone_audio.py tests/test_voice_translation_pipeline.py tests/test_voice_translation_realtime.py`
  - Result: `All checks passed!`
- `poetry run pytest -q`
  - Result: `94 passed, 1 warning in 3.19s`
  - Warning: existing Starlette/httpx deprecation warning from FastAPI testclient import.
- `git diff --check`
  - Result: no whitespace errors.

## Requirement Mapping

- `Niveles seguros de mezcla de voz traducida`
  - Covered by settings tests asserting defaults `passthrough=1.0`, `ducked=0.03`, `max_ducked=0.12`, `output=0.75`.
  - Covered by pipeline tests asserting requested ducking `0.6` is capped to `0.12` and both requested/applied values are logged.
- `Protección básica contra clipping de salida`
  - Covered by PCM limiter tests and realtime receiver tests asserting hot PCM is limited before writing to the virtual microphone.
- `Rechazo de fuentes de captura peligrosas`
  - Covered by source validation tests rejecting `.monitor`, `so_ai_translated_mic`, and `so_ai_translated_mic_sink.monitor`.

## Residual Risk

- The limiter applies to the translated output stream before PulseAudio mixes it with passthrough. It is not a final post-mix limiter, so the conservative ducking default remains important.
- A live Slack/Meet smoke test with headphones is still needed to confirm perceived echo and balance in the real call path.
