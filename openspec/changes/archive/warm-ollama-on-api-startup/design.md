## Design

Add `OLLAMA_WARMUP_ON_STARTUP` to local inference API settings.

When enabled, the FastAPI lifespan builds the configured runtime adapter and calls `warmup()` before serving normal requests. For Ollama, warm-up sends a minimal `/api/generate` request with:

- the configured model
- a single whitespace prompt
- `num_predict=1`
- the configured `OLLAMA_KEEP_ALIVE`

This loads the model and refreshes its residency timer without changing the normal text generation endpoint.

Remote OpenAI-compatible providers implement `warmup()` as a no-op because remote model residency is controlled by the provider.

## Risks

- API startup takes longer when warm-up is enabled.
- Keeping a model resident consumes RAM/VRAM while the keep-alive window is active.
- Warm-up does not remove normal prompt evaluation and token generation time.

## Validation

- Unit-test the Ollama warm-up payload.
- Run focused tests for the API, Ollama adapter, and Windows text adapters.
- Run linting.
