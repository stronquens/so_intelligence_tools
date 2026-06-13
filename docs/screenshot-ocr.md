# Screenshot OCR

Status: Planned / specced.

Screenshot OCR is intended to capture a region of the screen, extract visible text, and copy the exact extracted text to the clipboard.

## Current Building Blocks

The local inference API already exposes:

```text
POST /v1/image/extract-text
```

The CLI also exposes:

```bash
poetry run so-intelligence-tools extract-image-text --image-path /path/to/image.png --reasoning-mode off
```

## Intended Workflow

The planned desktop workflow is:

1. Press a global shortcut.
2. Select a screen region.
3. Send the image to the local API.
4. Copy extracted text to the clipboard.
5. Show a desktop notification.

## Runtime

This capability is designed for local/on-prem execution when the configured model supports vision through Ollama. It can also work through an API-compatible provider if the provider supports image inputs.

## Limitations

- The polished shortcut workflow is not implemented yet.
- Exact OCR quality depends on the configured model.

