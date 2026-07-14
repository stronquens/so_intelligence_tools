## ADDED Requirements

### Requirement: Linux Whisper backend bootstrap
The system SHALL prepare the faster-whisper Docker backend when installing Linux push-to-talk dictation integration.

#### Scenario: Linux desktop integration installs dictation
- **WHEN** the user runs the Linux desktop integration installer
- **THEN** the system SHALL ensure `docker/whisper-server/.env` exists
- **AND** the system SHALL run the faster-whisper Docker Compose service before enabling the dictation listener service.

#### Scenario: User installs only the dictation service
- **WHEN** the user runs the standalone push-to-talk dictation service installer
- **THEN** the system SHALL ensure the faster-whisper Docker backend is started before enabling the service.
