## ADDED Requirements

### Requirement: Shortcut map introspection
The system SHALL provide a way to inspect the effective keyboard shortcuts by platform.

#### Scenario: User lists all shortcuts
- **WHEN** the user runs the shortcut map command without filters
- **THEN** the system SHALL show supported Linux, Windows and desktop-overlay shortcut entries
- **AND** each entry SHALL include the feature, platform, configured shortcut, configuration source and activation mechanism.

#### Scenario: User filters shortcuts by platform
- **WHEN** the user requests a specific platform shortcut map
- **THEN** the system SHALL show only entries for that platform.

#### Scenario: Shortcut is visual but not globally registered
- **WHEN** a shortcut belongs to desktop overlay settings rather than an OS listener
- **THEN** the system SHALL identify it separately from active OS-level shortcuts.
