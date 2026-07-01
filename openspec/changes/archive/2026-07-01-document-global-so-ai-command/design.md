# Design

The documentation will present `so-ai` as a user-level convenience command that points to the Poetry-managed CLI inside this repository:

```text
~/.local/bin/so-ai -> /home/sciling/Escritorio/so_intelligence_tools/.venv/bin/so-intelligence-tools
```

`~/.local/bin` is already on the Linux user's `PATH`, so the command is available in new terminal sessions and VS Code integrated terminals after shell startup. The docs keep `poetry run so-intelligence-tools` for repo-local setup commands where appropriate, but recommend `so-ai` for per-window Codex controls that are commonly run from another project.
