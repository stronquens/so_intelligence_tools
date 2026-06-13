# Security And Secrets

This repository is public. Treat all paid provider credentials and local private configuration as secrets.

## Never Commit

- `.env`
- API keys
- LiteLLM virtual keys
- debug audio recordings
- private transcripts
- local provider URLs that should not be public

## Use `.env.example`

Use `.env.example` for safe defaults and empty placeholders. Real values belong in `.env`.

```bash
cp .env.example .env
```

## Check Before Publishing

Useful local checks:

```bash
git status --short
git diff --cached
rg -n "OPENAI_API_KEY|LITELLM_VIRTUAL_KEY|sk-[A-Za-z0-9]|api[_-]?key|secret|token" .
```

For Git history review:

```bash
git log --all --stat
git grep -n "OPENAI_API_KEY\\|LITELLM_VIRTUAL_KEY\\|api_key\\|secret\\|token" $(git rev-list --all)
```

If a real key was committed at any point, rotate it with the provider. Removing it from the latest commit is not enough once it has entered history.

## Debug Audio

Voice translation debug recordings can contain private speech. Keep them under ignored cache paths such as:

```text
~/.cache/so_intelligence_tools/voice_translation_debug_audio
```

Do not move recordings into the repository.

