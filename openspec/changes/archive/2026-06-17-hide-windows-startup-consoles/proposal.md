## Why

Windows Startup currently launches the local API and shortcut listener through `.cmd` files. They keep visible console windows open after login, which makes the desktop feel noisy even though the services are meant to run resident in the background.

## What Changes

- Replace Windows Startup `.cmd` launchers for the API and shortcut listener with hidden user-level launchers.
- Preserve user-level installation with no administrator requirement.
- Redirect background process output to per-service log files so failures remain diagnosable without visible terminals.
- Update Windows documentation to explain that the processes are still required for startup shortcuts, but the windows are not.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `keyboard-shortcuts`: Windows shortcut listener Startup install should create a hidden launcher with logs instead of a visible command window.
- `local-inference-api`: Windows API Startup install should create a hidden launcher with logs instead of a visible command window.

## Impact

- Affected code: `src/so_intelligence_tools/infrastructure/windows_startup.py`
- Affected tests: `tests/test_windows_startup.py`
- Affected docs: `docs/windows-support.md`
- Affected local system state: reinstalling Startup entries will replace visible `.cmd` launchers with hidden `.vbs` launchers in the current user's Startup folder.
