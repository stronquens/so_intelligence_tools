# Validation

## Automated Checks

Focused tests:

```powershell
poetry run pytest tests/test_windows_text_adapters.py tests/test_ollama_adapter.py tests/test_api.py -q
```

Result:

```text
21 passed, 1 warning
```

Full suite:

```powershell
poetry run pytest -q
```

Result:

```text
116 passed, 1 skipped, 1 warning
```

Lint:

```powershell
poetry run ruff check src tests
```

Result:

```text
All checks passed!
```

## Windows Runtime Smoke

Restarted the local inference API with:

```env
OLLAMA_KEEP_ALIVE=24h
OLLAMA_WARMUP_ON_STARTUP=true
```

Verified status:

```powershell
Invoke-RestMethod http://127.0.0.1:8010/status
```

Result:

```text
status: ok
ollama_reachable: true
configured_model: gemma4-e2b-longctx:latest
configured_model_available: true
```

Verified the model is resident after API startup, then restarted the API and confirmed the
residency timer refreshed:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/ps
```

Result included:

```text
name: gemma4-e2b-longctx:latest
expires_at: 2026-06-14T22:53:43...
```

This confirms startup warm-up loaded the configured model and refreshed the keep-alive window.
