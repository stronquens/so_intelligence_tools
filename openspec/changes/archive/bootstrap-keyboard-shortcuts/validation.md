## Automated Validation

Validation for this change combined:

- unit tests for the shortcut registry
- unit tests for the Linux text selection and insertion adapters
- unit tests for the Wayland guard on the shortcut listener
- full project regression tests after integration

### Executed Commands

- `poetry run pytest -q`
- `poetry run python -m compileall src tests`

### Results

- `23 passed`
- compile step completed successfully

## Real Validation

This environment is currently running on `Wayland`, so validation was split in two parts.

### 1. Real selected-text-correction action through command adapters

Executed flow:

1. Start local API:
   - `poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8000`
2. Run the selected-text-correction action through the new runtime wiring:
   - `poetry run so-intelligence-tools run-selected-text-correction`
3. Provide Linux command adapters through environment variables for the validation run:
   - `LINUX_READ_SELECTION_COMMAND="printf 'Holaa mundoo desde linux'"`
   - `LINUX_REPLACE_SELECTION_COMMAND="cat > <tmpfile>"`

Observed result:

- the action completed successfully against the real local backend
- corrected text written by the replacement adapter:
  - `Hola mundo desde Linux`

### 2. Real shortcut listener startup behavior in this environment

Executed flow:

- `poetry run so-intelligence-tools listen-shortcuts`

Observed result:

- the CLI failed cleanly with a user-facing message:
  - `La primera implementación de atajos globales está orientada a Linux X11; Wayland requiere un adapter específico.`

### 3. Real GNOME custom shortcut installation on this Wayland desktop

Executed flow:

- `poetry run so-intelligence-tools install-gnome-selected-text-shortcut`
- verification with `gsettings get` on:
  - `org.gnome.settings-daemon.plugins.media-keys custom-keybindings`
  - `org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/so-intelligence-tools-selected-text-correction/ name`
  - `... command`
  - `... binding`

Observed result:

- the custom shortcut path was registered in GNOME
- the shortcut name was stored as `Selected Text Correction`
- the binding was stored as `'<Primary>space'`
- the command now points to the project-local executable:
  - `/home/sciling/Escritorio/so_intelligence_tools/.venv/bin/so-intelligence-tools run-selected-text-correction`

## Known Limits

- The first shortcut listener implementation is Linux-first and explicitly X11-oriented.
- Wayland currently fails with explicit feedback on the Python listener instead of attempting unreliable global shortcut capture.
- On GNOME Wayland the supported validation path is the native custom shortcut integration.
- On GNOME Wayland, selected-text replacement depends on `wl-clipboard` plus `ydotool`/`ydotoold`; `wtype` was tested and this GNOME compositor rejects its virtual keyboard protocol.
- A debug wrapper is installed for the GNOME shortcut while validating this change. It writes early execution traces to `~/.cache/so_intelligence_tools/selected_text_correction.log`.
- Similar Wayland-first projects use compositor-managed shortcuts and a cascade of injection backends such as portal, `wtype`, `ydotool`, and clipboard. The current GNOME 42 environment needs the `ydotoold` fallback because `wtype` is rejected by the compositor.
- Ubuntu 22.04's packaged `ydotoold` uses `/tmp/.ydotool_socket`; if GNOME inherits `YDOTOOL_SOCKET=/run/user/<uid>/.ydotool_socket`, the wrapper and Python adapter must override it.
- On this Ubuntu 22.04 GNOME Wayland machine, the selected text can be captured and corrected through the LLM, but automatic replacement is not reliable. The supported manual fallback is to leave the corrected text on the clipboard. The recommended full automatic path for this first iteration is the installed `Ubuntu on Xorg` session.
- Real desktop-wide end-to-end validation of the global shortcut action still depends on a manually focused GUI application and was prepared but not fully automated.
