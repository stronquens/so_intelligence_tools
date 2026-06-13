## Summary

Add a user-level Windows Startup installer for the local inference API.

## Motivation

Windows selected text correction depends on the local inference API being available after login. The shortcut listener already had a Startup installer, but the API launcher was only created manually on the test machine. The setup should be reproducible from the repository CLI.

## Scope

- Add `install-windows-api-startup`.
- Write `so-intelligence-tools-api.cmd` into the current user's Startup folder.
- Use the project `.venv` and configured host/port.
- Document Windows startup setup.
