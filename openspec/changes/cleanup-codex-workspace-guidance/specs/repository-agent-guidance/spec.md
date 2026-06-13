## ADDED Requirements

### Requirement: Current Codex Guidance

The repository SHALL provide Codex guidance that reflects the active workflow, existing project files, and supported validation commands.

#### Scenario: Agent reads local guidance

- **WHEN** a Codex session inspects `.codex/AGENTS.md`
- **THEN** the guidance references root `AGENTS.md`, OpenSpec, Poetry, pytest, Ruff, and existing repository paths

### Requirement: Codex-Compatible Agent Templates

The repository SHALL keep `.codex/agents/` files as Codex-compatible runtime delegation prompt templates that do not require missing files or obsolete workflows.

#### Scenario: Repository is checked for stale agent harness references

- **WHEN** `.codex` files are searched for old harness paths
- **THEN** the agent templates do not require `feature_list.json`, `progress/current.md`, `.claude/agents`, or `CHECKPOINTS.md`

### Requirement: Manual Preflight Helper

The repository SHALL provide a manual `.codex/init.sh` preflight that uses the current project toolchain.

#### Scenario: Developer runs the preflight

- **WHEN** `.codex/init.sh` is executed from the repository root
- **THEN** it checks required project files and runs available Poetry-based lint, test, and OpenSpec validation commands without referencing obsolete files

### Requirement: Codex Subagent Guidance

The repository SHALL explain that `.codex/agents/` contains reusable prompt templates for runtime Codex subagents, not auto-loaded role definitions.

#### Scenario: Contributor wants parallel agent work

- **WHEN** a contributor reads `.codex/AGENTS.md`
- **THEN** they can see how Codex should use explorer or worker subagents without relying on removed Claude-specific files
