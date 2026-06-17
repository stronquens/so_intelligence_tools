## MODIFIED Requirements

### Requirement: Windows shortcut listener startup entry
The system SHALL provide a user-level Windows startup entry for the selected text correction shortcut listener.

#### Scenario: The user installs Windows shortcut startup
- **WHEN** the user runs the Windows shortcut startup installer
- **THEN** the system SHALL create a Startup folder launcher that launches the shortcut listener from the project virtual environment
- **AND** the launcher SHALL run without leaving a visible terminal window open
- **AND** the launcher SHALL write process output to a diagnostic log file
- **AND** the installer SHALL NOT require administrator privileges.

#### Scenario: The user starts a new Windows session
- **WHEN** the Startup entry exists
- **THEN** Windows SHALL be able to start the shortcut listener after user login.
