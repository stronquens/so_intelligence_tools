## 1. OpenSpec Scope

- [x] 1.1 Create proposal, design and task artifacts for Windows selected-text shortcut support.
- [x] 1.2 Define explicit out-of-scope items for Electron, Task Scheduler and audio shortcuts.

## 2. Shortcut Listener

- [x] 2.1 Add Windows shortcut listener support.
- [x] 2.2 Add a platform-aware listener factory.
- [x] 2.3 Update `listen-shortcuts` to compose runtime and listener by platform.
- [x] 2.4 Add Windows default selected-text correction shortcut setting.

## 3. Startup Integration

- [x] 3.1 Add a Windows Startup installer for the shortcut listener.
- [x] 3.2 Add CLI command to install the Windows startup entry.

## 4. Documentation And Tests

- [x] 4.1 Add tests for listener selection and Windows startup script generation.
- [x] 4.2 Update Windows support docs with run/install instructions.
- [x] 4.3 Add Windows focused-input `Ctrl+A` fallback when no text is selected.
- [x] 4.4 Add shortcut action cooldown to avoid repeated paste/correction events.

## 5. Validation

- [x] 5.1 Run full pytest.
- [x] 5.2 Run ruff.
- [x] 5.3 Record validation evidence and residual risks in `validation.md`.
