## MODIFIED Requirements

### Requirement: Warm Piper TTS Runtime
The system SHALL provide a local Dockerized Piper TTS runtime that loads the configured voice at startup and remains warm while the container is running.

#### Scenario: Service starts and becomes ready
- **WHEN** the user starts the Piper TTS Docker service
- **THEN** the service SHALL load the configured Piper voice before reporting ready
- **AND** the service SHALL expose a health endpoint that reports readiness.

#### Scenario: Service is stopped
- **WHEN** the Piper TTS Docker service is stopped
- **THEN** voice output SHALL be considered disabled
- **AND** normal text-only assistant workflows SHALL continue without blocking.

#### Scenario: Linux user logs in after reboot
- **WHEN** the Linux user session starts after reboot
- **THEN** the system SHALL run a user-level voice runtime startup service
- **AND** that service SHALL ensure the Piper TTS Docker runtime is started for Codex voice output.
