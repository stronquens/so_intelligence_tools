## Validation

Date: 2026-06-13

### Commands

```bash
openspec validate cleanup-codex-workspace-guidance --strict
.codex/init.sh
rg -n "feature_list|progress/current|progress/history|CHECKPOINTS|\\.claude/agents|docs/architecture|docs/conventions|docs/verification|scripts/demo_orchestration|python3 -m unittest" .codex -S
for d in .codex/skills/*; do if [ -f "$d/SKILL.md" ]; then python3 .codex/skills/skill-creator/scripts/quick_validate.py "$d"; fi; done
rg -n "AskUserQuestion|TodoWrite|subagent_type|Task tool|tools:\\s*(Read|Write|Edit|Bash)|\\.claude|Claude|claude" .codex/skills .codex/AGENTS.md -S
```

### Results

- `openspec validate cleanup-codex-workspace-guidance --strict` passed.
- All local `.codex/skills/*/SKILL.md` files passed `quick_validate.py`.
- `.codex/init.sh` passed:
  - `poetry check`
  - `poetry run ruff check src tests scripts`
  - `poetry run pytest` with 101 passed and 1 external deprecation warning
  - `openspec validate --all --strict`
- The stale-reference scan found no removed harness paths.
- The Claude-specific tool/reference scan found no matches.
- `.codex/AGENTS.md` documents Codex subagents as runtime explorer/worker delegation and points to `.codex/agents/` prompt templates.
