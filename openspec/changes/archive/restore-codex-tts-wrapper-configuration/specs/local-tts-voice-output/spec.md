## ADDED Requirements

### Requirement: VS Code Codex voice bridge activation
The system SHALL configure the VS Code Codex extension to launch its app-server through the repository TTS wrapper when Codex task-boundary speech is enabled.

#### Scenario: Voice bridge is enabled
- **WHEN** the user enables Codex voice output in VS Code
- **THEN** the user-level `chatgpt.cliExecutable` setting SHALL resolve to the executable repository TTS wrapper
- **AND** a newly loaded Codex extension process SHALL register an active voice session and forward supported lifecycle events to the selected local TTS backend.

#### Scenario: Existing VS Code process predates the setting
- **WHEN** the wrapper setting is restored while VS Code already has a Codex app-server running
- **THEN** the VS Code window SHALL be reloaded before runtime activation is considered complete.

#### Scenario: Wrapper cannot be launched
- **WHEN** the configured wrapper path is missing, non-executable, or cannot resolve a bundled Codex CLI
- **THEN** validation SHALL report the bridge as inactive
- **AND** the system SHALL NOT report a healthy TTS server alone as proof that Codex voice output is operational.
