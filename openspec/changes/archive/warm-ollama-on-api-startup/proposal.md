## Summary

Warm the configured Ollama model when the local inference API starts.

## Motivation

Windows shortcut correction now works, but the first request after startup can feel slow because Ollama loads the model on demand. Moving that load to API startup makes the first user-triggered correction feel closer to a warm request.

## Scope

- Add optional Ollama warm-up during `local-inference-api` lifespan startup.
- Keep warm-up controlled by `.env`.
- Preserve existing generation behavior and `keep_alive` handling.
- Document the setting for Windows shortcut usage.

## Out of Scope

- Installing a full Windows service manager.
- Choosing or downloading a different model.
- Eliminating normal generation latency after the model is already loaded.
