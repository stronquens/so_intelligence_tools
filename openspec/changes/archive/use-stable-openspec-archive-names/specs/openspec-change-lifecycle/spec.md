## ADDED Requirements

### Requirement: Stable archived change identity
The repository SHALL archive each completed change at `openspec/changes/archive/<change-name>/` without adding a date or another mutable prefix to its directory name.

#### Scenario: Archive a completed change
- **WHEN** a completed change named `<change-name>` is archived
- **THEN** its artifacts are moved to `openspec/changes/archive/<change-name>/`
- **AND** the archived directory preserves the change name exactly

### Requirement: Lossless archive migration
The repository MUST preserve all tracked artifacts and evidence when migrating an archived change from a dated path to its stable path.

#### Scenario: Migrate a dated archive
- **WHEN** an archive named `YYYY-MM-DD-<change-name>` has no destination collision
- **THEN** the complete directory is renamed to `<change-name>`
- **AND** its file contents remain unchanged

### Requirement: Explicit archive collision handling
The archive workflow MUST stop before overwriting an existing destination and SHALL consolidate directories only when they are verified to represent the same change without loss of artifacts or evidence.

#### Scenario: Stable destination already exists
- **WHEN** `archive/<change-name>/` already exists
- **THEN** the workflow stops before moving or overwriting files
- **AND** reports the collision for content comparison or functional renaming

### Requirement: Durable archive references
Versioned documentation and workflows SHALL use the stable archive path whenever they reference an archived change.

#### Scenario: Archived artifact is referenced
- **WHEN** documentation links to a file stored inside an archived change
- **THEN** the link uses `openspec/changes/archive/<change-name>/...`
