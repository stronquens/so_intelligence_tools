## MODIFIED Requirements

### Requirement: Windows press-and-hold dictation shortcut
The system SHALL provide a Windows global press-and-hold shortcut for local dictation.

#### Scenario: Dictation shortcut press
- **WHEN** the Windows dictation listener is running
- **AND** the user presses the configured dictation shortcut
- **THEN** the system SHALL start only the dictation action
- **AND** it SHALL ignore repeated press events while dictation is already active.

#### Scenario: Dictation shortcut release
- **WHEN** dictation is active from the Windows dictation shortcut
- **AND** the user releases the shortcut
- **THEN** the system SHALL stop only the active dictation action.

#### Scenario: Dictation shortcut avoids native Windows dictation
- **WHEN** Windows dictation shortcuts are configured by default
- **THEN** the system SHALL use `Ctrl+Shift+Space` for project dictation
- **AND** this SHALL avoid the known `Ctrl+Space` operating-system shortcut collision.

### Requirement: Shortcut map introspection
The system SHALL provide a way to inspect the effective keyboard shortcuts by platform.

#### Scenario: User lists all shortcuts
- **WHEN** the user runs the shortcut map command without filters
- **THEN** the system SHALL show supported Linux, Windows and desktop-overlay shortcut entries
- **AND** each entry SHALL include the feature, platform, configured shortcut, configuration source and activation mechanism.

#### Scenario: User filters shortcuts by platform
- **WHEN** the user requests a specific platform shortcut map
- **THEN** the system SHALL show only entries for that platform.

#### Scenario: Windows overlay shortcut is listed
- **WHEN** the user requests the Windows shortcut map
- **THEN** the system SHALL include the main overlay launcher shortcut
- **AND** it SHALL identify `Ctrl + Alt + A` as the Windows shortcut that opens or toggles the overlay.

#### Scenario: Shortcut is visual but not globally registered
- **WHEN** a shortcut belongs to desktop overlay settings rather than an OS listener
- **THEN** the system SHALL identify it separately from active OS-level shortcuts.

#### Scenario: Dictation shortcut is listed with the current default
- **WHEN** the user requests Linux, Windows, or desktop shortcut maps with default settings
- **THEN** push-to-talk dictation SHALL be shown as `Ctrl + Shift + Space`.

### Requirement: User-facing shortcut documentation
The repository SHALL keep user-facing shortcut documentation aligned with the implemented operating-system and desktop shortcut behavior.

#### Scenario: Documentation describes active shortcuts
- **WHEN** a shortcut becomes operational or changes ownership between features
- **THEN** README, AGENTS and relevant `docs/` pages SHALL identify the active key combination, platform, feature and configuration source.
