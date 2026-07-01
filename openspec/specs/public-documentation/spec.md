# public-documentation Specification

## Purpose
TBD - created by archiving change expand-public-english-docs. Update Purpose after archive.
## Requirements
### Requirement: English Documentation Index

The repository SHALL provide an English `docs/README.md` that links to setup, architecture, feature, troubleshooting, security, and contribution documentation.

#### Scenario: Reader opens docs folder

- **WHEN** a reader opens `docs/README.md`
- **THEN** they can navigate to the major operational and feature guides without reading Spanish content

### Requirement: Feature Documentation Coverage

The repository SHALL document the current operational behavior and maturity of implemented, experimental, and planned user-facing capabilities.

#### Scenario: Reader evaluates a feature

- **WHEN** a reader opens a feature guide
- **THEN** the guide states what works now, the runtime/backend expectations, useful commands, and important limitations

### Requirement: Public Security Guidance

The repository SHALL document how secrets and paid provider API keys should be handled for public repository usage.

#### Scenario: Contributor configures providers

- **WHEN** a contributor needs API keys or provider configuration
- **THEN** the docs instruct them to keep real secrets in `.env` and out of Git history

### Requirement: Platform-specific operational documentation
The repository SHALL distinguish Linux and Windows operational state when a feature has platform-specific shortcuts, services, runtimes, validation evidence, or limitations.

#### Scenario: Reader compares Linux and Windows setup
- **WHEN** a reader opens setup, shortcut, configuration, or feature documentation for a cross-platform workflow
- **THEN** the documentation SHALL identify Linux and Windows behavior separately where they differ.

#### Scenario: Dictation documentation mentions validation or performance
- **WHEN** push-to-talk dictation documentation describes validation, latency, model choice, or runtime setup
- **THEN** it SHALL state whether the evidence applies to Linux, Windows, or both.
