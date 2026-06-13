## Why

The repository-level `.codex` folder contains stale agent guidance, hooks, and helper scripts from an earlier workflow. Those files reference missing project files and obsolete validation commands, which can mislead future Codex sessions and contributors.

## What Changes

- Replace `.codex/AGENTS.md` with concise, current guidance for this repository.
- Replace obsolete `.codex/agents/` subagent definitions with Codex-compatible runtime delegation prompt templates.
- Replace `.codex/init.sh` with a lightweight repository check aligned with Poetry, pytest, Ruff, and OpenSpec.
- Remove `.codex/settings.json` hooks that execute stale validation commands.
- Keep local `.codex/skills/` because they support the current OpenSpec workflow.

## Capabilities

### New Capabilities

- `repository-agent-guidance`: Repository-local Codex guidance and validation helpers remain accurate, scoped, and non-conflicting with the project workflow.

### Modified Capabilities

None.

## Impact

- Affected files are limited to `.codex/` and this OpenSpec change.
- No product code, runtime API, user services, or dependencies change.
- Future Codex sessions should receive less conflicting guidance, safer validation commands, and reusable subagent prompt templates.
