## MODIFIED Requirements

### Requirement: Electron overlay launcher view
The desktop application SHALL provide an Electron/Vue overlay launcher view based on the stored design reference, and its settings panel SHALL expose functional controls instead of static mock controls.

#### Scenario: Overlay opens settings panel from the settings button
- **WHEN** the overlay launcher is visible
- **AND** the user clicks the settings button
- **THEN** it SHALL show a settings panel with shortcut rows and toggles for startup and always-visible behavior
- **AND** it SHALL load the current persisted desktop settings.

#### Scenario: User edits a shortcut row
- **WHEN** the settings panel is visible
- **AND** the user clicks a shortcut edit button
- **THEN** the row SHALL allow entering a new keyboard combination
- **AND** the displayed shortcut SHALL update before saving.

#### Scenario: User closes settings
- **WHEN** the settings panel is visible
- **AND** the user clicks the back or close control
- **THEN** the settings panel SHALL close without closing the launcher.
