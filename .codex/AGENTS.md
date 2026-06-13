# Codex Workspace Notes

This folder contains repository-local Codex affordances. The canonical working
agreement for the project lives in the root `AGENTS.md`; read that first.

## What To Keep In Mind

- Use OpenSpec before implementation. Create or select a change under
  `openspec/changes/`, define scope, design, specs, tasks, and validation.
- Use Poetry for Python work. Do not install Python dependencies globally for
  this project.
- Prefer `poetry run pytest`, `poetry run ruff check src tests scripts`, and
  `openspec validate <change> --strict` for verification.
- Keep `.env` and other local secrets out of version control.
- Treat Linux as the current target while keeping OS-specific behavior isolated.

## Local Skills

The `.codex/skills/` directory is intentionally tracked because this repository
uses the local OpenSpec skills during planning, implementation, validation, and
archiving.

Useful skills:

- `openspec-propose`: create a new change.
- `openspec-apply-change`: implement tasks from a change.
- `openspec-validate-change`: validate a change and capture evidence.
- `openspec-sync-specs`: sync completed delta specs.
- `openspec-archive-change`: archive completed changes.

## Subagents

Codex can use subagents when the active session exposes multi-agent tools. They
are runtime workers spawned by Codex, not Markdown agent profiles loaded from
`.codex/agents/`.

Use subagents for bounded parallel work:

- `explorer`: answer specific codebase questions.
- `worker`: implement a clearly scoped slice with explicit file ownership.

When using workers, split tasks by disjoint files or modules, tell each worker
that other edits may exist in the worktree, and review/integrate their changes
before committing.

Reusable Codex delegation prompts live in `.codex/agents/`. They are not
auto-loaded role definitions; they are prompt templates for the main Codex agent
to copy or adapt when spawning runtime `explorer` or `worker` subagents.

Do not use legacy agent frontmatter or hard-coded tool declarations in these
files. Keep them plain Markdown, scoped, and compatible with Codex runtime
delegation.

## Manual Preflight

Run this from the repository root when you want a quick workspace sanity check:

```bash
.codex/init.sh
```

The script is a helper, not a replacement for targeted validation. Feature work
should still run the tests and OpenSpec validation relevant to that change.
