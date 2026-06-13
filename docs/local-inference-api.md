# Local Inference API

Status: Working.

The local inference API is a FastAPI service that gives desktop tools one stable local interface regardless of whether the underlying model runs in Ollama or behind an OpenAI-compatible proxy.

## Start The API

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010 --reload
```

Or use the installed user service:

```bash
systemctl --user start so-intelligence-tools-api.service
```

On Windows, install the current user's Startup launcher:

```powershell
cd C:\Dev\Active\so_intelligence_tools
poetry run so-intelligence-tools install-windows-api-startup
```

For the current session, run:

```powershell
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010
```

## Health

```bash
curl http://127.0.0.1:8010/health
```

Expected shape:

```json
{
  "status": "ok",
  "service": "local-inference-api"
}
```

## Runtime Status

```bash
curl http://127.0.0.1:8010/status
```

This reports provider reachability and whether the configured model appears available.

With Ollama warm-up enabled, API startup also loads the configured model and refreshes its keep-alive window:

```env
OLLAMA_MODEL=gemma4-e2b-longctx:latest
OLLAMA_KEEP_ALIVE=24h
OLLAMA_WARMUP_ON_STARTUP=true
```

## Text Generation

```bash
curl http://127.0.0.1:8010/v1/text/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Correct this sentence: helllo wrld",
    "reasoning_mode": "off",
    "max_output_tokens": 128,
    "temperature": 0
  }'
```

`reasoning_mode` accepts the project modes used by the desktop tools. For Ollama, `off` and `low` use the fast path.

## Image Text Extraction

```bash
curl http://127.0.0.1:8010/v1/image/extract-text \
  -F image=@/path/to/screenshot.png \
  -F reasoning_mode=off
```

This endpoint is intended for screenshot OCR workflows.

## Providers

Supported providers:

- `ollama`
- `litellm_proxy`

See [Configuration](configuration.md) for environment variables.

