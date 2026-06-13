# Codex Subagent Prompt Templates

Codex subagents are spawned at runtime when the active session exposes
multi-agent tools. This directory contains reusable prompt templates for that
runtime delegation.

These files are not automatic role loaders. The main Codex agent should read or
adapt them when delegating bounded work to an `explorer` or `worker`.

## Available Templates

- [Explorer](explorer.md): read-only investigation and codebase questions.
- [Worker](worker.md): scoped implementation in owned files or modules.
- [Reviewer](reviewer.md): review, validation, and risk checks.
- [Leader](leader.md): bounded coordination and task splitting.
- [Implementer](implementer.md): compatibility role name for scoped worker implementation.

## Rules

- Keep templates plain Markdown.
- Do not add legacy agent frontmatter or hard-coded tool declarations.
- Always define ownership and scope before spawning a worker.
- Tell workers that other edits may exist and must not be reverted.
- Review subagent output before integrating or committing.
