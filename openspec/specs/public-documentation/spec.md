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

