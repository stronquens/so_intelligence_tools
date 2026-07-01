## ADDED Requirements

### Requirement: Dictation sessions do not overlap
The push-to-talk dictation runner SHALL prevent a new dictation session from starting while a previous session is still finalizing transcription or text insertion.

#### Scenario: User presses again while previous release is finalizing
- **WHEN** a dictation release is still finalizing
- **AND** the user presses the dictation shortcut again
- **THEN** the runner SHALL NOT start a second capture
- **AND** text from the previous recording SHALL NOT be inserted into the new recording's result state.

### Requirement: Faster-whisper HTTP warm runtime semantics
The system SHALL keep the faster-whisper HTTP runtime warm before listening, while treating each dictation as a buffered transcription finalized after release.

#### Scenario: Dictation listener starts
- **WHEN** the dictation listener starts
- **THEN** it SHALL check the faster-whisper HTTP server readiness before accepting shortcut input.

#### Scenario: User releases the dictation shortcut
- **WHEN** the user releases the dictation shortcut
- **THEN** the runner SHALL stop capture after post-roll
- **AND** it SHALL send the captured utterance for final transcription.
