## ADDED Requirements

### Requirement: Codex Turn Boundary Speech
The system SHALL speak Codex task boundary cues exactly once per active turn and only for real terminal turn events.

#### Scenario: Duplicate turn start events
- **WHEN** a Codex voice listener receives repeated turn-start events for the same active turn
- **THEN** it SHALL speak the task-start cue only once.

#### Scenario: Tool call inside active turn
- **WHEN** a Codex voice listener receives a tool, function, or command lifecycle event while a turn is active
- **THEN** it SHALL speak the configured lifecycle cue when the current detail mode allows it
- **AND** it SHALL NOT speak the task-end cue for that intermediate event.

#### Scenario: Real turn completion
- **WHEN** a Codex voice listener receives a true turn completion event
- **THEN** it SHALL clear pending queued speech according to the configured completion behavior
- **AND** it SHALL speak the task-end cue once.

#### Scenario: Turn completion without explicit start
- **WHEN** a Codex voice listener receives a true turn completion event without having observed a turn-start event first
- **THEN** it SHALL still speak the task-end cue once when the current detail mode allows lifecycle speech.
