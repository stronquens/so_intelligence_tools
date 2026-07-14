## ADDED Requirements

### Requirement: CPU model benchmark evidence
The project SHALL evaluate CPU dictation model changes with measured latency and quality evidence before changing the default model.

#### Scenario: Benchmark runs candidate models
- **WHEN** a CPU dictation model benchmark is run
- **THEN** it SHALL record model name, startup readiness time, transcription time, audio duration, realtime factor, and transcript text.

#### Scenario: Benchmark avoids persistent model cache pollution
- **WHEN** candidate models are benchmarked in Docker
- **THEN** temporary benchmark containers and volumes SHALL be removed after each candidate
- **AND** the existing production `whisper-server` container and volume SHALL remain unchanged.

#### Scenario: Reference transcript is unavailable
- **WHEN** no human reference transcript is provided
- **THEN** the benchmark SHALL label quality metrics against the current large model as pseudo-reference evidence.
