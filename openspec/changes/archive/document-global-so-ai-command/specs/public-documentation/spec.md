## MODIFIED Requirements

### Requirement: Platform-specific operational documentation
The repository SHALL distinguish Linux and Windows operational state when a feature has platform-specific shortcuts, services, runtimes, validation evidence, or limitations.

#### Scenario: Linux user controls voice from another project
- **WHEN** a Linux user needs to run local tool commands from a terminal whose current project is not `so_intelligence_tools`
- **THEN** the documentation SHALL show the persistent `so-ai` command
- **AND** it SHALL explain that the command points to the repository-managed CLI.
