# Selected Text Correction

Status: Working on Linux/GNOME/X11.

Selected text correction lets you select text in another application, press a global shortcut, and replace the selection with corrected text while preserving the original language.

## Shortcut

Default:

```text
Ctrl + Alt + C
```

Configured by:

```env
GNOME_SELECTED_TEXT_CORRECTION_BINDING=<Primary><Alt>c
```

## Runtime

This feature uses:

- Linux text selection and clipboard adapters.
- The local inference API.
- Ollama or an OpenAI-compatible remote provider behind the local API.

## Manual Command

```bash
poetry run so-intelligence-tools run-selected-text-correction --debug
```

Debug log:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/selected_text_correction.log
```

## Notes

- X11 is currently the most reliable session type.
- On X11, the tool reads the primary selection and uses the clipboard as the stable replacement path.
- Wayland support depends on compositor support and tools such as `wl-clipboard`, `wtype`, and `ydotool`.

