## ADDED Requirements

### Requirement: Ollama startup warm-up

The local inference API SHALL support optional startup warm-up for the configured Ollama model.

#### Scenario: Warm-up is enabled

- **GIVEN** `OLLAMA_WARMUP_ON_STARTUP` is enabled
- **AND** the configured provider is Ollama
- **WHEN** the local inference API starts
- **THEN** it SHALL send a minimal generation request for the configured model
- **AND** it SHALL use the configured Ollama keep-alive value.

#### Scenario: Warm-up fails

- **GIVEN** startup warm-up is enabled
- **AND** Ollama is unreachable
- **WHEN** the local inference API starts
- **THEN** it SHALL log the warm-up failure
- **AND** it SHALL continue starting so `/status` can report the degraded runtime.
