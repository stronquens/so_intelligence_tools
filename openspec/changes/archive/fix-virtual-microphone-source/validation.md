# Validation

## Summary

Validated that the voice translation virtual microphone now creates a user-facing input source (`so_ai_translated_mic`) backed by an internal mix sink (`so_ai_translated_mic_sink`). Runtime messages and docs now instruct users to select the input source as microphone and keep their normal speaker output.

## Automated

- `poetry run pytest tests/test_voice_translation_virtual_microphone_audio.py tests/test_voice_translation_pipeline.py tests/test_system_audio_translation_app.py tests/test_voice_translation_realtime.py -q`
  - Result: `20 passed in 0.39s`
- `poetry run pytest -q`
  - Result: `89 passed, 1 warning in 3.26s`
  - Warning: existing Starlette/httpx deprecation warning from FastAPI testclient import.
- `poetry run ruff check src/so_intelligence_tools/voice_translation_virtual_microphone src/so_intelligence_tools/system_audio_translation/app.py tests/test_voice_translation_virtual_microphone_audio.py tests/test_voice_translation_pipeline.py tests/test_system_audio_translation_app.py tests/test_voice_translation_realtime.py`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: no whitespace errors.

## Requirement Mapping

- `Micrófono virtual seleccionable por aplicaciones externas`
  - Covered by tests asserting `module-remap-source` is loaded with `source_name=so_ai_test_mic`.
  - Covered by app tests asserting user-facing status names `so_ai_test`, not `so_ai_test.monitor`.
- `Implementación inicial Linux PulseAudio`
  - Covered by tests asserting `module-null-sink` is created as `so_ai_test_mic_sink`.
  - Covered by tests asserting `pacat` writes to the internal sink and both modules unload on stop.
  - Covered by tests asserting the internal sink is unloaded if remapped source creation fails.
- `Control desde la ventana de traducción en tiempo real`
  - Covered by system audio app tests asserting passthrough/translation messages point at the selectable input source.

## Residual Risk

- Slack/Zoom/Meet enumeration was not manually exercised in this environment. The PulseAudio contract is now the correct one for those apps: a remapped source is published as the microphone, while the null sink remains an internal mix target.
