# Validation

Date: 2026-07-01.
Host: local Linux workstation.

## Commands Run

```bash
so-ai --help
so-ai codex-voice-sessions
poetry run openspec validate document-global-so-ai-command --strict
poetry run openspec validate public-documentation --strict
```

## Results

- `so-ai` resolves from `~/.local/bin` and runs the project CLI.
- `so-ai codex-voice-sessions` lists active Codex voice sessions from multiple working directories, confirming it can be used outside this repository.
- The OpenSpec change and updated `public-documentation` spec validate successfully.
