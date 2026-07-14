## ADDED Requirements

### Requirement: Independent realtime turn publication
The system SHALL publish each completed realtime translation turn without allowing an earlier incomplete turn to block later completed turns.

#### Scenario: Earlier turn has no original transcript
- **WHEN** an earlier realtime turn has translated text but no original transcript and a later turn has both original and translated final text
- **THEN** the system SHALL publish the later complete turn to accumulated history
- **AND** it SHALL keep or finalize the earlier incomplete turn independently.

#### Scenario: Original and translation complete in either order
- **WHEN** the original transcript and translated response for a turn arrive in either order
- **THEN** the system SHALL correlate them by provider turn identity
- **AND** it SHALL publish the resulting history block exactly once.

#### Scenario: Consecutive turns have identical translation text
- **WHEN** two distinct provider turns produce the same translated text
- **THEN** the system SHALL preserve both turns in history
- **AND** it SHALL use provider identity rather than text equality for deduplication.

### Requirement: Realtime residual turn finalization
The system SHALL account for pending visible realtime content when a receiver stops, reconnects, or is cancelled.

#### Scenario: Connection ends with complete pending content
- **WHEN** a realtime connection ends with a pending turn containing original and translated final or partial text
- **THEN** the system SHALL publish that turn to history before discarding connection state.

#### Scenario: Connection ends with translation only
- **WHEN** a realtime connection ends with translated text but no usable original transcript
- **THEN** the system SHALL publish a translation-only history block
- **AND** it SHALL record that fallback finalization in the session log.

#### Scenario: Connection ends with original only
- **WHEN** a realtime connection ends with original text but no translated text
- **THEN** the system SHALL record the incomplete turn in the session log
- **AND** it SHALL NOT present untranslated content as a completed translation block.

### Requirement: Realtime audio queue observability
The system SHALL record when bounded realtime audio buffering discards captured audio.

#### Scenario: Pending audio queue is full
- **WHEN** a captured audio chunk arrives while the bounded pending queue is full
- **THEN** the system SHALL retain its configured memory bound
- **AND** it SHALL record a cumulative dropped-audio event for diagnosis.
