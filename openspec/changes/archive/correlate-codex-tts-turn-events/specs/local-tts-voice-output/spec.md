## MODIFIED Requirements

### Requirement: Codex Turn Boundary Speech
The system SHALL speak Codex task boundary cues exactly once per correlated active turn and only for terminal events belonging to that same Codex thread and turn.

#### Scenario: Duplicate turn start events
- **WHEN** a Codex voice listener receives repeated turn-start events for the same active turn
- **THEN** it SHALL speak the task-start cue only once.

#### Scenario: Tool call inside active turn
- **WHEN** a Codex voice listener receives a tool, function, or command lifecycle event belonging to the active turn
- **THEN** it SHALL speak the configured lifecycle cue when the current detail mode allows it
- **AND** it SHALL NOT speak the task-end cue for that intermediate event.

#### Scenario: Real turn completion
- **WHEN** a Codex voice listener receives a terminal turn event whose `threadId` and `turnId` match the active correlated turn
- **THEN** it SHALL clear pending queued speech according to the configured completion behavior
- **AND** it SHALL speak the task-end cue once.

#### Scenario: Completion belongs to another turn
- **WHEN** a terminal event identifies a different thread or turn from the active correlated turn
- **THEN** the listener SHALL ignore that terminal event for speech purposes
- **AND** it SHALL NOT flush active text, clear queued speech, or reset the active turn.

#### Scenario: Duplicate correlated completion
- **WHEN** the listener receives a repeated terminal event for a turn whose completion cue was already emitted
- **THEN** it SHALL NOT emit another task-end cue.

#### Scenario: Turn completion without explicit start
- **WHEN** a Codex voice listener receives a true terminal event without having observed a turn-start event first
- **THEN** it SHALL speak the task-end cue once when the current detail mode allows lifecycle speech
- **AND** it SHALL deduplicate subsequent terminal events carrying the same identifiers.

#### Scenario: Identified background progress
- **WHEN** message or action lifecycle events identify a different turn from the active correlated turn
- **THEN** those events SHALL NOT mark the active turn as having assistant output
- **AND** they SHALL NOT be read as progress for the active turn.

#### Scenario: Legacy events lack identifiers
- **WHEN** the listener receives supported legacy lifecycle events without usable thread and turn identifiers
- **THEN** it SHALL apply the conservative order-based fallback
- **AND** existing identifier-less integrations SHALL remain functional.
