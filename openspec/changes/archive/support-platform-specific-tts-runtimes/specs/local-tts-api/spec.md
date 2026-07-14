## MODIFIED Requirements

### Requirement: Platform-aware default local TTS endpoint
Generic local TTS clients SHALL target the endpoint associated with the resolved local TTS backend when no explicit base URL is configured.

#### Scenario: Linux client uses default TTS settings
- **WHEN** a local TTS client runs on Linux without an explicit base URL
- **THEN** it SHALL resolve Piper and target `http://127.0.0.1:9010`
- **AND** requests SHALL remain compatible with the shared speech endpoint.

#### Scenario: Windows client uses default TTS settings
- **WHEN** a local TTS client runs on Windows without an explicit base URL
- **THEN** it SHALL resolve Chatterbox and target `http://127.0.0.1:9011`
- **AND** requests SHALL remain compatible with the shared speech endpoint.

#### Scenario: Client explicitly overrides the endpoint
- **WHEN** a local TTS client is configured with `LOCAL_TTS_BASE_URL`
- **THEN** it SHALL target that URL independently of the resolved platform backend.
