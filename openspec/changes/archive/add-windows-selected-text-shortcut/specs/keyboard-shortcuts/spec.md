# Delta Spec

## ADDED Requirements

### Requirement: Windows selected text correction shortcut listener
The system SHALL provide an initial Windows global shortcut listener for selected text correction.

#### Scenario: The listener runs on Windows
- **WHEN** the shortcut listener is started on Windows
- **THEN** it SHALL register a Windows-compatible global shortcut for selected text correction
- **AND** it SHALL execute the selected-text correction action through the platform-aware runtime.

#### Scenario: The user presses the Windows correction shortcut
- **WHEN** the listener is running
- **AND** the user presses the configured selected-text correction shortcut
- **THEN** the system SHALL run only the selected text correction action.
- **AND** repeated hotkey events inside the configured cooldown window SHALL be ignored.

#### Scenario: The user presses the Windows correction shortcut without selected text
- **WHEN** the listener is running
- **AND** focus is in a text input that supports normal Windows text shortcuts
- **AND** no text is selected
- **AND** the user presses the configured selected-text correction shortcut
- **THEN** the system SHALL attempt `Ctrl+A` followed by copy before reporting missing selected text.

### Requirement: Windows shortcut listener startup entry
The system SHALL provide a user-level Windows startup entry for the selected text correction shortcut listener.

#### Scenario: The user installs Windows shortcut startup
- **WHEN** the user runs the Windows shortcut startup installer
- **THEN** the system SHALL create a Startup folder command file that launches the shortcut listener from the project virtual environment
- **AND** the installer SHALL NOT require administrator privileges.

#### Scenario: The user starts a new Windows session
- **WHEN** the Startup entry exists
- **THEN** Windows SHALL be able to start the shortcut listener after user login.
