## Validation

Date: 2026-06-16

## Checks

- `poetry run pytest tests/test_windows_startup.py -q`
  - Result: passed, 6 tests.
- `poetry run ruff check src/so_intelligence_tools/infrastructure/windows_startup.py src/so_intelligence_tools/infrastructure/windows_background_launcher.py tests/test_windows_startup.py`
  - Result: passed.
- `openspec validate hide-windows-startup-consoles --strict`
  - Result: passed.
- Reinstalled current user Startup entries:
  - `so-intelligence-tools-api.vbs`
  - `so-intelligence-tools-shortcuts.vbs`
  - Confirmed previous `.cmd` entries are absent from the user Startup folder.
- Relaunched both `.vbs` entries from the Startup folder.
  - API process started and `/status` returned `status: ok`.
  - Shortcut listener process started.
  - No Windows Script Host path error appeared after launching via the `.vbs` file path directly.

## Notes

- Windows shows a parent process from the project `.venv` and a child process from the base Python installation. This is expected for the local virtual environment on this machine; only the child API process owns port `8010`.
- Logs are written under `%LOCALAPPDATA%\so_intelligence_tools\logs`.
