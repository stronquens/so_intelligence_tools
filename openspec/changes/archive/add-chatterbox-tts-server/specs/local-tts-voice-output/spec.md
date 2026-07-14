## ADDED Requirements

### Requirement: Warm Chatterbox TTS Runtime
The system SHALL provide a local Dockerized Chatterbox TTS runtime that loads the configured es-ES model at startup and remains warm while the container is running.

#### Scenario: Service starts and becomes ready
- **WHEN** the user starts the Chatterbox TTS Docker service
- **THEN** the service SHALL load the configured Chatterbox es-ES model and voice presets before reporting ready
- **AND** it SHALL expose a health endpoint that reports readiness.

#### Scenario: Service is stopped
- **WHEN** the Chatterbox TTS Docker service is stopped
- **THEN** GPU-backed voice output SHALL be considered disabled
- **AND** normal text-only assistant workflows SHALL continue without blocking.

### Requirement: Chatterbox lifecycle commands
The system SHALL provide CLI lifecycle commands for the Chatterbox TTS runtime.

#### Scenario: User starts Chatterbox TTS
- **WHEN** the user runs the Chatterbox TTS ensure command
- **THEN** the system SHALL create missing local service configuration from an example file, start the Docker Compose service, and wait for the health endpoint to report ready.

#### Scenario: User stops Chatterbox TTS
- **WHEN** the user runs the Chatterbox TTS stop command
- **THEN** the system SHALL stop the Docker Compose service so GPU memory can be reclaimed.

#### Scenario: User checks Chatterbox TTS status
- **WHEN** the user runs the Chatterbox TTS status command
- **THEN** the system SHALL report whether the Chatterbox TTS service is ready.

### Requirement: Chatterbox integration boundary
Codex voice hooks and OpenClaw SHALL be able to use Chatterbox TTS through the same local HTTP API without relying on private runtime internals.

#### Scenario: Codex voice hooks target Chatterbox
- **WHEN** the Codex voice listener is configured with the Chatterbox service base URL
- **THEN** it SHALL send visible speech text to the Chatterbox speech endpoint using the configured per-session voice.

#### Scenario: Windows Codex wrapper targets Chatterbox
- **WHEN** the Windows VS Code/Codex extension is configured to use the local Codex TTS wrapper command
- **THEN** the wrapper SHALL resolve the real bundled Windows Codex CLI, proxy app-server output back to the extension, and send visible events to Chatterbox through the local listener.

#### Scenario: Windows Codex Desktop monitor targets Chatterbox
- **WHEN** the standalone Codex Desktop app writes visible assistant messages to local session JSONL files
- **THEN** the Desktop session monitor SHALL tail new visible assistant messages, skip hidden reasoning and non-message events, and send the cleaned text to Chatterbox.
- **AND** the monitor SHALL support persistent voice and reading-detail configuration through the project settings or equivalent command-line options.

#### Scenario: OpenClaw targets Chatterbox
- **WHEN** OpenClaw is configured to call the Chatterbox service base URL
- **THEN** it SHALL be able to request `male` or `female` speech by passing the same `voice` parameter.

### Requirement: Chatterbox-only retained TTS path
The active project SHALL keep Chatterbox as the retained local TTS backend and remove discarded Piper/Kokoro/Qwen/NeuTTS benchmark service paths from active code and documentation.

#### Scenario: User asks for active TTS setup
- **WHEN** the user reads project setup documentation
- **THEN** the documentation SHALL point to Chatterbox for local TTS
- **AND** it SHALL distinguish Linux and Windows support status.

#### Scenario: User invokes TTS lifecycle commands
- **WHEN** the user lists or invokes local TTS lifecycle commands
- **THEN** the active CLI SHALL expose Chatterbox lifecycle commands
- **AND** it SHALL NOT expose Piper lifecycle commands.
