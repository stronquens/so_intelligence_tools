# local-tts-api Specification

## Purpose

Define benchmark and service-shape requirements for local text-to-speech backends before a concrete runtime is selected.

## Requirements

### Requirement: Local TTS backend benchmark evidence
The project SHALL evaluate local text-to-speech backends with measured CPU latency, Spanish quality notes, and runtime feasibility before choosing a default local TTS service.

#### Scenario: Benchmark runs a candidate backend
- **WHEN** a local TTS candidate is benchmarked
- **THEN** the benchmark SHALL record backend name, model identifier, startup readiness time, synthesis time, generated audio duration, realtime factor, output file path, and runtime notes.

#### Scenario: Benchmark avoids persistent model cache pollution
- **WHEN** a TTS candidate downloads model weights or runtime artifacts
- **THEN** those artifacts SHALL be scoped to a temporary Docker volume or cache path
- **AND** they SHALL be removed after the benchmark unless the user explicitly chooses to keep that backend.

#### Scenario: Candidate is not CPU-feasible
- **WHEN** a candidate requires GPU-only features or cannot complete a minimal CPU synthesis test within the benchmark limits
- **THEN** the benchmark SHALL record it as not CPU-feasible with the reason
- **AND** it SHALL continue evaluating the remaining candidates.

### Requirement: Local TTS service shape
The future local TTS service SHALL expose a stable text-to-audio interface independent of the selected backend.

#### Scenario: Client requests Spanish speech
- **WHEN** a client submits Spanish text to the local TTS service
- **THEN** the service SHALL synthesize an audio file or audio stream with the configured backend
- **AND** it SHALL report backend/model metadata with the result.
