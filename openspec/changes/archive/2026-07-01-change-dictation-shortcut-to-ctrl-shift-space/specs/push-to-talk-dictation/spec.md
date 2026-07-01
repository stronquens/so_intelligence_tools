## MODIFIED Requirements

### Requirement: Windows local push-to-talk dictation
The system SHALL provide local push-to-talk dictation on Windows using the configured local ASR runtime.

#### Scenario: User holds the Windows dictation shortcut
- **WHEN** the Windows dictation listener is running
- **AND** the user holds `Ctrl + Shift + Space`
- **THEN** the system SHALL start capturing microphone audio
- **AND** it SHALL stream or buffer captured audio chunks for the configured local ASR transcriber.

#### Scenario: User releases the Windows dictation shortcut
- **WHEN** the Windows dictation listener is capturing microphone audio
- **AND** the user releases any key in the configured dictation shortcut
- **THEN** the system SHALL stop microphone capture after the configured post-roll
- **AND** it SHALL finalize the ASR session.

#### Scenario: Faster-whisper HTTP runtime is selected
- **WHEN** `PUSH_TO_TALK_DICTATION_RUNTIME` is `faster_whisper_http`
- **THEN** the system SHALL send captured dictation audio to the configured OpenAI-compatible `/v1/audio/transcriptions` endpoint
- **AND** it SHALL insert the final transcript after the user releases the shortcut.

## ADDED Requirements

### Requirement: Dictation shortcut includes Shift support
The press-and-hold dictation listener SHALL support shortcuts that include the `Shift` modifier.

#### Scenario: User holds Ctrl Shift Space
- **WHEN** the dictation listener is configured with `Ctrl + Shift + Space`
- **AND** the user holds Ctrl, Shift, and Space together
- **THEN** the system SHALL start dictation capture.
