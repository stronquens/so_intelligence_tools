# overlay-action-dispatch Specification

## Purpose
TBD - created by archiving change make-overlay-actions-functional. Update Purpose after archive.
## Requirements
### Requirement: Overlay commands are dispatched through Electron
The desktop overlay SHALL dispatch tool card actions through a typed Electron IPC bridge.

#### Scenario: Renderer sends a tool command
- **WHEN** the user clicks a functional overlay tool card
- **THEN** the renderer SHALL send a command containing the tool action identifier through the preload bridge
- **AND** Electron main SHALL return a structured result with a status and message.

#### Scenario: Command is not implemented
- **WHEN** the user clicks a tool card whose backend action is not wired yet
- **THEN** the system SHALL return a pending result
- **AND** the overlay SHALL show user-visible pending feedback instead of silently doing nothing.

### Requirement: Overlay shows command status
The desktop overlay SHALL show immediate status feedback for command execution.

#### Scenario: Command starts
- **WHEN** a tool command is sent
- **THEN** the overlay SHALL show a running state for that command.

#### Scenario: Command completes
- **WHEN** Electron returns a successful command result
- **THEN** the overlay SHALL show a success message.

#### Scenario: Command fails
- **WHEN** Electron returns a failed command result
- **THEN** the overlay SHALL show a failure message.

