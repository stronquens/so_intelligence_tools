# keyboard-shortcuts Delta

## MODIFIED Requirements

### Requirement: Shortcut map introspection
The system SHALL provide a way to inspect the effective keyboard shortcuts by platform.

#### Scenario: Windows overlay shortcut is listed
- **WHEN** the user requests the Windows shortcut map
- **THEN** the system SHALL include the main overlay launcher shortcut
- **AND** it SHALL identify `Ctrl + Alt + A` as the Windows shortcut that opens or toggles the overlay.
