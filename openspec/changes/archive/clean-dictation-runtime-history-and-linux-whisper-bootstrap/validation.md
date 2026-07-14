## Validation Summary

Status: passed on 2026-06-17.

## Evidence

- Repository-wide search for retired dictation runtime identifiers returned no matches.
- `poetry run pytest tests/test_user_services.py tests/test_faster_whisper_http.py tests/test_windows_push_to_talk_dictation.py tests/test_push_to_talk_dictation_session.py tests/test_shortcut_map.py -q`
  - Result: 21 passed.
- `poetry run ruff check src/so_intelligence_tools/infrastructure/user_services.py src/so_intelligence_tools/cli/main.py src/so_intelligence_tools/push_to_talk_dictation tests/test_user_services.py tests/test_faster_whisper_http.py tests/test_windows_push_to_talk_dictation.py`
  - Result: all checks passed.
- `openspec validate --all --strict`
  - Result: 20 passed, 0 failed before archive.
