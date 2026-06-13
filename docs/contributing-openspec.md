# OpenSpec Contribution Workflow

This project uses OpenSpec to keep product decisions explicit and reviewable.

## Rule Of Thumb

Before implementing meaningful behavior, create or select a change under:

```text
openspec/changes/
```

Each change should contain:

- `proposal.md`: why the change exists and what is in scope
- `design.md`: technical decisions and trade-offs
- `specs/**/spec.md`: behavior requirements and scenarios
- `tasks.md`: implementation checklist
- `validation.md`: durable evidence of what was checked

## Common Flow

```bash
openspec new change "my-change-name"
openspec status --change "my-change-name" --json
openspec validate my-change-name --strict
```

After implementation, update tasks and validation evidence before archiving.

## Repository Skills

Local Codex skills live in:

```text
.codex/skills/
```

The OpenSpec skills are intentionally tracked so Codex sessions can follow the same workflow in this repository.

