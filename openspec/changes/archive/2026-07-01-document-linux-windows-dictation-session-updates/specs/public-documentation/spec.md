## ADDED Requirements

### Requirement: Platform-specific operational documentation
The repository SHALL distinguish Linux and Windows operational state when a feature has platform-specific shortcuts, services, runtimes, validation evidence, or limitations.

#### Scenario: Reader compares Linux and Windows setup
- **WHEN** a reader opens setup, shortcut, configuration, or feature documentation for a cross-platform workflow
- **THEN** the documentation SHALL identify Linux and Windows behavior separately where they differ.

#### Scenario: Dictation documentation mentions validation or performance
- **WHEN** push-to-talk dictation documentation describes validation, latency, model choice, or runtime setup
- **THEN** it SHALL state whether the evidence applies to Linux, Windows, or both.
