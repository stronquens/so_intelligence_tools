## Context

The project already has `ShortcutActionRegistry` and a Linux listener backed by `pynput.keyboard.GlobalHotKeys`. Windows can reuse most of that shape. The important design boundary is that listener selection belongs in infrastructure, while actions remain application/runtime composed.

## Goals / Non-Goals

**Goals**

- make selected text correction triggerable by a Windows global shortcut
- keep Linux listener behavior stable
- provide user-level startup persistence without admin rights
- keep the implementation small and testable

**Non-Goals**

- replacing the Linux GNOME shortcut path
- building a full Windows service manager
- routing shortcuts through Electron
- supporting every existing capability shortcut on Windows

## Decisions

Use native Win32 `RegisterHotKey` for the Windows listener.
Reason: manual validation showed the `pynput` listener process could die after the hotkey fired on this Windows environment. `RegisterHotKey` keeps the implementation small while avoiding that reliability issue.

Keep `LinuxShortcutListener` and add `WindowsShortcutListener`.
Reason: Linux has a Wayland guard and Windows does not. Separate classes keep platform rules explicit while sharing callback handling.

Add `build_shortcut_listener()`.
Reason: the CLI should not know which listener class each platform needs.

Add a Windows Startup `.cmd` installer.
Reason: it is user-level, reversible and does not require admin permissions. Task Scheduler can come later if this proves insufficient.

Use `Ctrl+Alt+C` as the Windows selected-text correction default.
Reason: it matches the public docs and GNOME shortcut default better than the older listener-only `<ctrl>+<space>` default.

## Proposed Architecture

```text
infrastructure/
  shortcut_listener.py
    BaseShortcutListener
    LinuxShortcutListener
    WindowsShortcutListener
    build_shortcut_listener()
  windows_startup.py
    WindowsShortcutStartupInstaller
```

CLI additions:

- `listen-shortcuts` becomes platform-aware
- `install-windows-shortcut-listener-startup` writes the Startup launcher

## Validation Strategy

- Unit-test Windows listener construction without starting OS hooks.
- Unit-test Linux Wayland guard remains in place.
- Unit-test Startup script generation.
- Run full pytest and ruff.

## Operational Notes

The listener must be running for `Ctrl+Alt+C` to work. After installing the startup entry, the user can either log out/in or run `poetry run so-intelligence-tools listen-shortcuts` manually for the current session.
