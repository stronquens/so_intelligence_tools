# Validation

## Confirmed Runtime

The active backend reported:

```json
{
  "configured_model": "eu/tensorix/deepseek/deepseek-v4-flash",
  "configured_model_available": true
}
```

This confirms the running instance was using DeepSeek through LiteLLM Proxy.

## Remote Proxy Discovery

The external enterprise LiteLLM Proxy was queried successfully through `/v1/models`.

A working subset of available models included:

- `eu/tensorix/deepseek/deepseek-v4-flash`
- `openai/gpt-4.1-mini`
- `eu/azure/openai/gpt-4.1`

The original configured value from the external project env:

- `litellm_proxy/eu/tensorix/deepseek/deepseek-v4-pro`

returned `400` with a proxy message indicating no healthy deployments were currently available for that model group.

## Local vs Remote Timing

Prompt used:

- system: `Corrige ortografía, gramática y puntuación del texto manteniendo el idioma original. Haz cambios mínimos, no traduzcas y no añadas explicación.`
- user: `voya  prioabr si ahora funciona de una vez`

Observed results:

- local `gemma4:e2b-it-qat` through project API:
  - about `1.665s`
  - output: `Voy a probar si ahora funciona de una vez.`

- remote `eu/tensorix/deepseek/deepseek-v4-flash` through direct LiteLLM Proxy:
  - about `0.781s`
  - output: `Voy a probar si ahora funciona de una vez.`

- remote `eu/tensorix/deepseek/deepseek-v4-flash` through the project API with `INFERENCE_PROVIDER=litellm_proxy`:
  - about `1.406s`
  - output: `Voy a probar si ahora funciona de una vez.`

- remote `eu/azure/openai/gpt-4.1` through direct LiteLLM Proxy:
  - about `1.361s`
  - output: `Voy a probar si ahora funciona de una vez.`

- remote `openai/gpt-4.1-mini` through direct LiteLLM Proxy:
  - about `2.737s`
  - output: `Voy a probar si ahora funciona de una vez.`

## Automated Tests

```bash
poetry run pytest -q
```

Result:

- `42 passed`
