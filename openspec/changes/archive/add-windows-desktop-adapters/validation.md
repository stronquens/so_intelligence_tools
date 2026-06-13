# Validation

## Summary

Implemented the first Windows desktop adapter slice for text-focused runner flows.

The change adds:

- Windows clipboard adapter using Win32 APIs through `ctypes`
- Windows keyboard automation adapter for copy, paste and direct text primitives
- Windows selected-text adapter using clipboard roundtrip preservation
- Windows text insertion adapter using clipboard plus paste
- best-effort Windows notification adapter
- platform-aware runtime composition
- selected text correction CLI runtime autodetection
- Windows support documentation
- Windows-portable test adjustments for GNOME shortcut tests and Unix socket assumptions

## Automated Validation

Ran the full Python test suite:

```bash
poetry run pytest -q
```

Result:

```text
107 passed, 1 skipped, 1 warning
```

The skipped test is the Unix-domain-socket toggle server test on a Python/platform combination without `socket.AF_UNIX`.

Ran linting across source and tests:

```bash
poetry run ruff check src tests
```

Result:

```text
All checks passed!
```

Ran a Windows runtime composition smoke check:

```bash
poetry run python -c "from so_intelligence_tools.infrastructure.runtime import build_runtime; r=build_runtime(platform_name='win32'); print(type(r).__name__)"
```

Result:

```text
WindowsRuntime
```

## Requirement Mapping

### Windows adapters for text-focused runner flows

Covered by:

- `tests/test_windows_text_adapters.py`
- `src/so_intelligence_tools/adapters/windows/clipboard.py`
- `src/so_intelligence_tools/adapters/windows/keyboard.py`
- `src/so_intelligence_tools/adapters/windows/text_selection.py`
- `src/so_intelligence_tools/adapters/windows/text_insertion.py`
- `src/so_intelligence_tools/adapters/windows/notification.py`

Validated behavior:

- selected text uses clipboard roundtrip and restores previous clipboard content
- empty prior clipboard is cleared after probing
- insertion writes replacement text to clipboard and sends paste
- Windows clipboard adapter rejects non-Windows platforms clearly

### Platform-aware runtime composition

Covered by:

- `src/so_intelligence_tools/infrastructure/runtime.py`
- `tests/test_windows_text_adapters.py`

Validated behavior:

- `build_runtime(platform_name="linux")` delegates to Linux runtime
- `build_runtime(platform_name="win32")` delegates to Windows runtime
- unsupported platforms raise `UnsupportedEnvironmentError`

### Windows shortcut installation remains separate

Covered by:

- `openspec/changes/add-windows-desktop-adapters/specs/keyboard-shortcuts/spec.md`
- `docs/windows-support.md`

Validated by documentation and scope boundaries. No Windows global shortcut installer was added in this change.

## Residual Risks

- Real focused-app automation can still be blocked by elevated windows, secure desktops, focus races or applications that intercept `Ctrl+C` / `Ctrl+V`.
- The first Windows notification adapter is deliberately best-effort and does not provide native toast notifications.
- Windows screenshot, startup integration, global shortcut registration and all audio workflows remain out of scope.

## Notes

`poetry install` was required before validation because the local `.venv` existed but did not yet contain dev dependencies such as `pytest` and `ruff`.
