# Validation

## Automated

```powershell
poetry run pytest tests/test_windows_startup.py -q
poetry run ruff check src tests
```

Result:

```text
Windows startup tests passed.
All checks passed.
```
