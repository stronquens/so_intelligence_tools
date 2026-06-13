## Design

Add `WindowsApiStartupInstaller` next to `WindowsShortcutStartupInstaller`.

The installer writes a `.cmd` file that:

- changes directory to the project root
- starts `.venv\Scripts\python.exe`
- runs `uvicorn --app-dir src local_inference_api.main:app`
- uses the configured API host and port

The command is user-level and requires no administrator privileges.
