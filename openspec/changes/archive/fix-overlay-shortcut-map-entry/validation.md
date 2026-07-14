# Validation

Validated on Windows from `C:\Dev\Active\so_intelligence_tools` on 2026-06-17.

## Commands

- `poetry run so-intelligence-tools show-shortcuts --platform windows`: passed; output includes `Open overlay` with `Ctrl + Alt + A`.
- `poetry run so-intelligence-tools show-shortcuts --platform desktop`: passed; output shows `Open overlay` with `Ctrl + Alt + A` and `Assistant` as `Sin asignar`.
- `poetry run pytest tests/test_shortcut_map.py -q`: passed, 4 tests.
- `poetry run ruff check src\so_intelligence_tools\infrastructure\shortcut_map.py tests\test_shortcut_map.py`: passed.
- `npm run test -- App.test.ts` from `desktop/`: passed, 15 tests.
- `npm run build` from `desktop/`: passed.
- `openspec validate fix-overlay-shortcut-map-entry --strict`: passed.
- `openspec validate --all --strict`: passed, 28 items.
- `openspec archive fix-overlay-shortcut-map-entry --yes`: passed; archived as `2026-06-17-fix-overlay-shortcut-map-entry`.
- `openspec validate --all --strict`: passed after archive and spec scenario restoration, 27 active items.

## Result

The shortcut map now lists the working Windows overlay launcher as `Ctrl + Alt + A`, desktop overlay defaults match it, and the previous Assistant shortcut collision is removed.
