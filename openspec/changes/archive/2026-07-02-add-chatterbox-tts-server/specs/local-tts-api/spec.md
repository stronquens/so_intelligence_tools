## ADDED Requirements

### Requirement: Chatterbox TTS service endpoints
The local TTS service SHALL support a Dockerized Chatterbox backend with stable health, metrics, and speech endpoints.

#### Scenario: Health reports loaded voices
- **WHEN** a client calls the Chatterbox TTS health endpoint after startup
- **THEN** the service SHALL report readiness, backend/model metadata, and the configured voice aliases.

#### Scenario: Metrics report runtime observations
- **WHEN** a client calls the Chatterbox TTS metrics endpoint
- **THEN** the service SHALL report synthesis request counts, failure counts, per-voice counts, latency observations, realtime-factor observations, and VRAM observations when available.

#### Scenario: Speech endpoint returns audio
- **WHEN** a client submits valid Spanish text to the Chatterbox speech endpoint
- **THEN** the service SHALL return playable WAV audio using the selected voice preset
- **AND** it SHALL reject unknown voices with a structured error listing available voices.

### Requirement: Chatterbox voice preset selection
The local TTS service SHALL allow Chatterbox voice presets to be selected per request without starting a separate container per voice.

#### Scenario: Male preset is selected
- **WHEN** a client requests speech with `voice` set to `male`
- **THEN** the service SHALL synthesize using the configured male Chatterbox es-ES preset.

#### Scenario: Female preset is selected
- **WHEN** a client requests speech with `voice` set to `female`
- **THEN** the service SHALL synthesize using the configured female Chatterbox es-ES voice clone preset chosen by the user.

#### Scenario: Voice aliases are localized
- **WHEN** a client requests speech with localized aliases such as `hombre` or `mujer`
- **THEN** the service SHALL resolve those aliases to the corresponding Chatterbox voice preset.

### Requirement: Default local TTS endpoint
Generic local TTS clients SHALL target the retained Chatterbox service by default.

#### Scenario: Client uses default TTS settings
- **WHEN** a local TTS client is created without an explicit base URL
- **THEN** it SHALL target `http://127.0.0.1:9011`
- **AND** requests SHALL remain compatible with the Chatterbox speech endpoint.
