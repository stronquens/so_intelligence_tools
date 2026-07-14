# Validation

Date: 2026-07-03.
Host: local Linux workstation.

## Commands Run

```bash
poetry run pytest tests/test_codex_voice_events.py tests/test_local_tts_client.py
poetry run python -m py_compile src/so_intelligence_tools/local_tts/codex_events.py src/so_intelligence_tools/local_tts/codex_voice.py scripts/codex-tts-wrapper.py
poetry run openspec validate fix-codex-voice-turn-boundaries --strict
```

## Results

- Focused TTS/event tests passed: 27 passed.
- Python compile checks passed.
- OpenSpec validation passed.

## Regression Coverage

- Repeated `turn/started` events speak "Inicio de tarea" once, preserving the
  established public cue while deduplicating repeated notifications.
- A premature `turn/completed` before the first tool call does not speak "Fin de tarea".
- Tool lifecycle events inside an active turn still speak in `actions` mode.
- A later real terminal turn event after an agent message speaks "Fin de tarea" once.
