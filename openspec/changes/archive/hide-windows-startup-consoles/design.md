## Context

The Windows integration uses a resident local API plus a resident global shortcut listener. The current Startup installers write `.cmd` files that run Python with `start /min`, which still leaves visible terminal windows after user login. The services should remain easy to install without administrator privileges and should stay debuggable when something fails.

## Goals / Non-Goals

**Goals:**

- Start the Windows API and shortcut listener at login without visible console windows.
- Keep launchers user-level and compatible with the current Startup-folder approach.
- Capture stdout/stderr in stable log files for troubleshooting.
- Reinstall the current machine's Startup entries after the installer changes.

**Non-Goals:**

- Replace Startup-folder launchers with Windows Services or Task Scheduler.
- Change the API host, port, model warm-up behavior, or shortcut bindings.
- Add live reload for overlay shortcut settings.

## Decisions

- Use `.vbs` Startup launchers with `WScript.Shell.Run(..., 0, False)`.
  - Rationale: VBScript is available on normal Windows installs, can hide the command window reliably, and does not require admin privileges.
  - Alternative considered: `pythonw.exe`. It hides the console but makes stdout/stderr handling less predictable for `uvicorn` and the listener.
  - Alternative considered: Task Scheduler. It can run hidden, but is heavier and adds more moving parts for a user-level desktop tool.

- Launch through `cmd.exe /c` from the `.vbs` and redirect output.
  - Rationale: The command can `cd` to the repo root, run the project `.venv` executable, and append stdout/stderr to log files with normal shell redirection.
  - Logs live under `%LOCALAPPDATA%\so_intelligence_tools\logs`.

- Remove old `.cmd` launchers during install.
  - Rationale: Reinstalling should not leave both visible and hidden launchers active, which would duplicate the API and listener processes.

## Risks / Trade-offs

- Hidden services are less obvious when running -> Mitigation: document Task Manager/process checks and log locations.
- Duplicate processes can remain from a previous visible startup until stopped or the user logs out -> Mitigation: after reinstalling on this machine, stop duplicate current-session processes and start a single hidden API/listener pair.
- VBScript availability could be restricted by policy on some machines -> Mitigation: keep the approach scoped to current user Startup and document that logs reveal launch failures when scripts are allowed to run.
