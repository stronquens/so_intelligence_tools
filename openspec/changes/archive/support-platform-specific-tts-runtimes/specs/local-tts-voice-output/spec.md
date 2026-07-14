## ADDED Requirements

### Requirement: Platform-aware local TTS backend selection
The system SHALL select a local TTS backend using explicit configuration with platform-aware defaults.

#### Scenario: Linux uses automatic backend selection
- **WHEN** the application runs on Linux with `LOCAL_TTS_BACKEND=auto`
- **THEN** the resolved local TTS backend SHALL be Piper
- **AND** the default speech API URL SHALL use the Piper port.

#### Scenario: Windows uses automatic backend selection
- **WHEN** the application runs on Windows with `LOCAL_TTS_BACKEND=auto`
- **THEN** the resolved local TTS backend SHALL be Chatterbox
- **AND** the default speech API URL SHALL use the Chatterbox port.

#### Scenario: Backend is explicitly configured
- **WHEN** the user configures `LOCAL_TTS_BACKEND` as `piper`, `chatterbox`, or `none`
- **THEN** the system SHALL honor that backend independently of the host platform
- **AND** an explicit `LOCAL_TTS_BASE_URL` SHALL override the backend default URL.

### Requirement: Warm Piper TTS Runtime
The system SHALL provide a Dockerized Piper TTS runtime as the supported lightweight Linux CPU voice-output path.

#### Scenario: Linux user starts Piper
- **WHEN** a Linux user starts the Piper TTS Docker service
- **THEN** the service SHALL load its configured voices before reporting ready
- **AND** it SHALL expose a local health endpoint and speech endpoint.

#### Scenario: Piper is stopped
- **WHEN** the Piper service is stopped
- **THEN** Piper-backed voice output SHALL be considered disabled
- **AND** normal text-only workflows SHALL continue without blocking.

### Requirement: Linux TTS login startup
The system SHALL start only the configured Linux TTS backend from the Linux voice-runtime user service.

#### Scenario: Linux default starts lightweight backend
- **WHEN** the Linux user logs in with automatic backend selection
- **THEN** the voice-runtime service SHALL ensure Piper
- **AND** it SHALL NOT start Chatterbox automatically.

#### Scenario: Linux user selects Chatterbox
- **WHEN** the Linux user explicitly configures Chatterbox as the local TTS backend
- **THEN** the voice-runtime service SHALL ensure Chatterbox instead of Piper.

#### Scenario: Linux user disables TTS startup
- **WHEN** the Linux user configures the local TTS backend as `none`
- **THEN** the voice-runtime service SHALL leave both TTS containers stopped or untouched
- **AND** it SHALL still allow non-TTS voice runtimes such as Whisper to start.

## MODIFIED Requirements

### Requirement: Local Speech API
The system SHALL expose a backend-compatible local HTTP API for converting visible text to speech audio.

#### Scenario: Text is synthesized
- **WHEN** a client sends valid text to the selected local speech endpoint
- **THEN** the selected Piper or Chatterbox service SHALL synthesize the text
- **AND** the service SHALL return playable audio with a content type and status code that clients can handle deterministically.

#### Scenario: Voice is selected per request
- **WHEN** the selected service is configured with multiple voice aliases
- **THEN** clients SHALL be able to select a supported voice by passing a `voice` parameter to the local speech endpoint
- **AND** the service SHALL use the requested voice without requiring a separate container per voice.

#### Scenario: Invalid or empty text is submitted
- **WHEN** a client sends empty or invalid text to the local speech endpoint
- **THEN** the selected service SHALL reject the request with a structured error
- **AND** the service SHALL NOT crash or restart its loaded model.
