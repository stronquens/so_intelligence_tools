## Context

The project now uses root `AGENTS.md`, OpenSpec changes, Poetry, pytest, Ruff, and local `.codex/skills/`. The existing `.codex/AGENTS.md`, `.codex/init.sh`, `.codex/settings.json`, and `.codex/agents/` files predate that workflow and reference files such as `feature_list.json`, `progress/current.md`, `CHECKPOINTS.md`, and `.claude/agents/`, which are not part of this repository.

## Goals / Non-Goals

**Goals:**

- Make `.codex` safe to keep in the public repository.
- Preserve useful local skills, especially the OpenSpec skills.
- Align the local validation helper with the actual project tooling.
- Remove duplicated or misleading agent definitions.

**Non-Goals:**

- Do not change application behavior.
- Do not introduce new automation hooks that can mutate the repository.
- Do not redesign the OpenSpec workflow.

## Decisions

- Keep `.codex/skills/` tracked for now. These skills are useful repo-local affordances and match the workflow described in `AGENTS.md`.
- Replace the old `.codex/agents/` files with plain Markdown prompt templates. The current Codex environment already receives root `AGENTS.md`; these templates are not auto-loaded roles, but they preserve reusable delegation patterns for runtime subagents.
- Document Codex subagents as runtime delegation tools rather than automatically loaded Markdown profiles.
- Replace `.codex/init.sh` rather than deleting it. A small manual preflight script is useful, but it must check the real project commands.
- Delete `.codex/settings.json`. The hook configuration is stale and may surprise future sessions by running outdated commands.

## Risks / Trade-offs

- Replacing old subagents preserves examples of multi-agent orchestration while avoiding broken instructions.
- The new `init.sh` is a best-effort preflight and does not replace targeted validation for feature work.
- Keeping generic skills increases repository size slightly, but avoids breaking local skill discovery.
