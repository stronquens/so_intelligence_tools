## Validation

- `poetry run pytest tests/test_shortcut_map.py -q`
  - Result: 4 passed.
- `poetry run ruff check src/so_intelligence_tools/infrastructure/shortcut_map.py src/so_intelligence_tools/cli/main.py tests/test_shortcut_map.py`
  - Result: all checks passed.
- `poetry run so-intelligence-tools show-shortcuts`
  - Result: printed Linux, Windows and desktop overlay shortcut maps from current settings.
- `poetry run so-intelligence-tools show-shortcuts --platform desktop`
  - Result: printed all desktop overlay shortcut settings and distinguished `ui-setting` from `planned`.
- `openspec validate add-shortcut-map-command --strict`
  - Result: valid.

## Notes

- The command reports effective Python `.env` settings for OS listeners.
- Desktop overlay shortcuts are listed separately because they are stored in Electron `desktop-settings.json` and are not all OS-level shortcuts.
- Changing `.env` still requires restarting already-running listeners/services.
