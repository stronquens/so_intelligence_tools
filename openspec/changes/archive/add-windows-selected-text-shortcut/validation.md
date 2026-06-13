# Validation

## Summary

Implemented initial Windows selected text correction shortcut support.

The change adds:

- `WindowsShortcutListener` backed by native Win32 `RegisterHotKey`
- platform-aware `build_shortcut_listener()`
- platform-aware `listen-shortcuts` CLI composition
- `WINDOWS_SELECTED_TEXT_CORRECTION_SHORTCUT`, defaulting to `<ctrl>+<alt>+c`
- `WindowsShortcutStartupInstaller`
- `install-windows-shortcut-listener-startup` CLI command
- documentation for running/installing the listener

## Automated Validation

Ran the full Python test suite:

```bash
poetry run pytest -q
```

Result:

```text
112 passed, 1 skipped, 1 warning
```

Ran linting:

```bash
poetry run ruff check src tests
```

Result:

```text
All checks passed!
```

## Smoke Checks

Verified Windows listener selection:

```bash
poetry run python -c "from so_intelligence_tools.infrastructure.shortcut_listener import build_shortcut_listener; from so_intelligence_tools.infrastructure.shortcut_actions import ShortcutActionRegistry; r=ShortcutActionRegistry(); print(type(build_shortcut_listener(shortcut_to_action={'<ctrl>+<alt>+c':'selected-text-correction'}, registry=r, platform_name='win32')).__name__)"
```

Result:

```text
WindowsShortcutListener
```

Verified the new CLI command appears in help:

```bash
poetry run so-intelligence-tools --help
```

Result included:

```text
listen-shortcuts
install-windows-shortcut-listener-startup
```

Installed the Windows Startup launcher:

```bash
poetry run so-intelligence-tools install-windows-shortcut-listener-startup
```

Result:

```text
Windows shortcut listener startup installed: C:\Users\arman\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\so-intelligence-tools-shortcuts.cmd
```

Verified launcher contents:

```cmd
@echo off
cd /d "C:\Dev\Active\so_intelligence_tools"
start "so_intelligence_tools shortcuts" /min "C:\Dev\Active\so_intelligence_tools\.venv\Scripts\python.exe" -m so_intelligence_tools listen-shortcuts
```

Started one listener for the current session and verified it stayed alive:

```text
python.exe -m so_intelligence_tools listen-shortcuts
```

## Follow-Up Fix

After manual testing, `Ctrl+Alt+C` did not replace selected text and the clipboard still contained the previous UUID-like value. The likely cause was the shortcut action firing while the physical `Ctrl+Alt+C` chord was still held, so the adapter's internal `Ctrl+C`/`Ctrl+V` automation could not reliably copy the active selection.

Fix applied:

- `BaseShortcutListener` now supports `action_delay_seconds`.
- `listen-shortcuts` passes `settings.shortcut_action_start_delay_seconds`.
- selected text correction launched from the listener writes debug evidence to `~/.cache/so_intelligence_tools/selected_text_correction.log`.

Re-validation after the fix:

```bash
poetry run pytest -q
poetry run ruff check src tests
```

Result:

```text
112 passed, 1 skipped, 1 warning
All checks passed!
```

## Second Follow-Up Fix

Further manual testing showed the shortcut still did not work because the listener process was dying after the hotkey fired.

Observed failures:

- `pynput` listener was replaced with a native Win32 `RegisterHotKey` listener for reliable Windows global hotkey registration.
- The clipboard adapter crashed with an access violation because Win32 clipboard function return types were not declared, causing pointer truncation on 64-bit Windows.
- The keyboard adapter returned Win32 error `87` because the `INPUT` union used by `SendInput` did not include the full Windows union shape.

Fixes applied:

- `WindowsShortcutListener` now uses native `RegisterHotKey` and a Win32 message loop.
- Windows clipboard APIs now declare `argtypes` and `restype`.
- Windows keyboard `INPUT` now includes `MOUSEINPUT`, `KEYBDINPUT` and `HARDWAREINPUT`, with pointer-sized `dwExtraInfo`.
- Shortcut handlers now catch unexpected exceptions and keep the listener alive.
- `shortcut_listener.log` records registration, trigger, completion and failure events.

Smoke evidence:

```text
[2026-06-13T22:33:14] registered shortcut=<ctrl>+<alt>+c action=selected-text-correction
[2026-06-13T22:33:15] triggered action=selected-text-correction
[2026-06-13T22:33:17] failed action=selected-text-correction error=No hay texto seleccionado.
```

The simulated hotkey reached the listener and failed only because the PowerShell simulation had no selected text, which is the expected behavior.

Re-validation after the second fix:

```text
114 passed, 1 skipped, 1 warning
All checks passed!
```

## Requirement Mapping

## Runtime Configuration Follow-Up

User logs showed that the shortcut and text capture were already working, but the action failed when calling Ollama:

```text
[2026-06-13T22:34:41] triggered action=selected-text-correction
[2026-06-13T22:34:43] failed action=selected-text-correction error=No se puede contactar con Ollama. Levanta el runtime local antes de enviar peticiones.
```

Applied local runtime configuration in `.env`:

```text
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
INFERENCE_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4-e2b-longctx:latest
OLLAMA_TIMEOUT_SECONDS=180
OLLAMA_KEEP_ALIVE=10m
WINDOWS_SELECTED_TEXT_CORRECTION_SHORTCUT=<ctrl>+<alt>+c
```

Verified Ollama and the local inference API:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/version
Invoke-RestMethod http://127.0.0.1:8010/status
```

Result:

```text
ollama_reachable: true
configured_model: gemma4-e2b-longctx:latest
configured_model_available: true
```

Verified CLI correction:

```powershell
poetry run so-intelligence-tools correct-text --text "voy a ahcer una ultima prueba a ver si funcioan" --reasoning-mode off
```

Result:

```text
Voy a hacer una última prueba a ver si funcionan.
```

Verified end-to-end Windows replacement with a temporary Tk text window. The probe selected this text, sent `Ctrl+Alt+C`, waited for the listener, and read the changed widget content:

```text
CHANGED=Voy a hacer una última prueba a ver si funcionan.
```

Listener evidence:

```text
[2026-06-13T22:42:34] triggered action=selected-text-correction
[2026-06-13T22:42:38] completed action=selected-text-correction
```

Selected-text debug evidence:

```text
[2026-06-13T20:42:35.392362+00:00] selected-text-correction captured-selection
selected='voy a ahcer una ultima prueba a ver si funcioan'
corrected=None
[2026-06-13T20:42:38.444183+00:00] selected-text-correction completed
selected='voy a ahcer una ultima prueba a ver si funcioan'
corrected='Voy a hacer una última prueba a ver si funcionan.'
```

## Focused Input Fallback Follow-Up

Added Windows fallback behavior for the case where the user presses the shortcut with focus in a text input but without selecting text first.

Behavior:

- first try the normal selected-text clipboard roundtrip
- if no selected text is copied quickly, send `Ctrl+A`
- copy again and correct the whole focused input

Automated coverage:

```powershell
poetry run pytest tests/test_windows_text_adapters.py -q
```

Covered by `test_windows_text_selection_selects_all_focused_input_when_no_text_is_selected`.

Real Windows smoke:

```text
CHANGED=Esto es una prueba sin texto seleccionado.
```

Listener evidence:

```text
[2026-06-13T22:51:35] triggered action=selected-text-correction
[2026-06-13T22:51:38] completed action=selected-text-correction
```

Selected-text debug evidence:

```text
[2026-06-13T20:51:36.891663+00:00] selected-text-correction captured-selection
selected='esto es una prueva sin texto selecionado'
corrected=None
[2026-06-13T20:51:38.603784+00:00] selected-text-correction completed
selected='esto es una prueva sin texto selecionado'
corrected='Esto es una prueba sin texto seleccionado.'
```

## Shortcut Cooldown Follow-Up

Manual use showed that repeated Windows hotkey events could queue back-to-back corrections, especially around chat inputs that clear after Enter. Added a per-action cooldown so repeated hotkey events immediately after a correction are ignored instead of running another copy/correction/paste cycle.

Automated coverage:

```powershell
poetry run pytest tests/test_shortcut_listener.py tests/test_windows_text_adapters.py -q
```

Result:

```text
16 passed
```

Lint:

```powershell
poetry run ruff check src tests
```

Result:

```text
All checks passed!
```

### Windows selected text correction shortcut listener

Covered by:

- `src/so_intelligence_tools/infrastructure/shortcut_listener.py`
- `src/so_intelligence_tools/cli/main.py`
- `tests/test_shortcut_listener.py`

Validated behavior:

- Windows platform selects `WindowsShortcutListener`
- Linux platform still selects `LinuxShortcutListener`
- unsupported platforms fail clearly

### Windows shortcut listener startup entry

Covered by:

- `src/so_intelligence_tools/infrastructure/windows_startup.py`
- `tests/test_windows_startup.py`

Validated behavior:

- Startup launcher is written to the selected Startup folder
- launcher starts `.venv\Scripts\pythonw.exe -m so_intelligence_tools listen-shortcuts`
- missing project virtualenv reports a configuration error

## Residual Risks

- The listener must be running for `Ctrl+Alt+C` to work. The Startup entry handles future logins, but it does not start a listener in the current session unless the user runs `poetry run so-intelligence-tools listen-shortcuts`.
- Native Win32 global hotkeys may not capture shortcuts in elevated apps, secure desktops or apps that intercept the same binding.
- The local inference API and Ollama must be running, and `OLLAMA_MODEL` must point at an installed local model.
- This change only wires selected text correction. Audio, screenshot and dictation shortcut paths remain future work on Windows.
