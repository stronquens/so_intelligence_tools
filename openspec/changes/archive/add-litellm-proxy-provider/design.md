# Design

## Summary

Introduce a provider boundary inside `local-inference-api` so the backend can choose between:

- `OllamaAdapter`
- `RemoteOpenAICompatibleAdapter`

The user-facing tools continue calling the same local FastAPI service, so `keyboard-shortcuts`, `selected-text-correction`, and other runners do not need provider-specific logic.

## Provider Selection

The provider is selected from `.env` using:

- `INFERENCE_PROVIDER=ollama`
- `INFERENCE_PROVIDER=litellm_proxy`

Remote mode also requires:

- `LITELLM_PROXY_URL`
- `LITELLM_VIRTUAL_KEY`
- `LITELLM_MODEL`

## API Contract

The FastAPI endpoints remain unchanged:

- `GET /health`
- `GET /status`
- `POST /v1/text/generate`
- `POST /v1/image/extract-text`

This keeps the existing Python runners stable.

## Remote Request Shape

The first remote implementation uses OpenAI-compatible `POST /v1/chat/completions`.

For text generation:

- `system` prompt -> system message
- user prompt -> user message
- `max_output_tokens` -> `max_tokens`

For image extraction:

- send a user message with text plus `image_url` content using a `data:` URL

## Status Semantics

`/status` still reports:

- configured model
- model availability
- provider reachability

The payload keeps the same top-level shape even though `ollama_version` is naturally `null` in remote mode.

## Validation Notes

During validation, the configured DeepSeek Pro model from the external project env had no healthy deployment on the proxy. A working remote comparison was performed with:

- `eu/tensorix/deepseek/deepseek-v4-flash`

Observed text-correction latency comparison:

- local `gemma4:e2b-it-qat`: about `1.665s`
- remote `eu/tensorix/deepseek/deepseek-v4-flash`: about `1.406s` through the project API
