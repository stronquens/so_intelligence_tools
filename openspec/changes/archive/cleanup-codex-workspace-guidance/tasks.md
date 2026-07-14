## 1. Planning

- [x] 1.1 Document the `.codex` cleanup scope in proposal, design, specs, and tasks.

## 2. Cleanup

- [x] 2.1 Replace `.codex/AGENTS.md` with current repository guidance.
- [x] 2.2 Replace `.codex/init.sh` with a Poetry/OpenSpec-aware manual preflight.
- [x] 2.3 Replace obsolete `.codex/agents/` files with Codex prompt templates and remove stale hook settings.

## 3. Validation

- [x] 3.1 Validate the OpenSpec change.
- [x] 3.2 Run the new `.codex/init.sh` helper.
- [x] 3.3 Confirm `.codex` no longer references the removed harness paths.
- [x] 3.4 Validate local skills with the Codex skill validator and remove Claude-specific tool references.
