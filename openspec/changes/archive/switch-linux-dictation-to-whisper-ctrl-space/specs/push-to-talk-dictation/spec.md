## MODIFIED Requirements

### Requirement: Press-and-hold dictation shortcut

The system SHALL provide a push-to-talk dictation listener that records while the configured shortcut is held and inserts recognized Spanish text into the focused field after release.

#### Scenario: Linux default shortcut starts dictation

- **WHEN** the Linux desktop integration is installed with default settings
- **THEN** the push-to-talk dictation listener uses `Ctrl + Shift + Space`

#### Scenario: Whisper runtime is checked before listening

- **WHEN** the Linux dictation service is installed
- **THEN** the faster-whisper Docker server is ensured before the listener is enabled

#### Scenario: Native Ubuntu shortcut conflict is cleared

- **WHEN** the Linux desktop integration is installed on a system exposing IBus `Ctrl + Space` hotkeys
- **THEN** the installer clears those conflicting hotkeys as best-effort cleanup for users who previously had dictation on `Ctrl + Space`
