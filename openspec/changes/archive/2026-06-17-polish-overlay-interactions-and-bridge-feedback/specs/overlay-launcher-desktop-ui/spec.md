## MODIFIED Requirements

### Requirement: Electron overlay launcher view
The desktop application SHALL provide an Electron/Vue overlay launcher view with clear interactive feedback for available and unavailable tool actions.

#### Scenario: User hovers or presses overlay controls
- **WHEN** the overlay launcher or settings panel is visible
- **AND** the user hovers or presses a tool card or control
- **THEN** the control SHALL provide visible motion or state feedback.

#### Scenario: User clicks an unwired placeholder tool
- **WHEN** the user clicks a tool card that is visible but not wired yet
- **THEN** the overlay SHALL show pending feedback
- **AND** it SHALL NOT expose a low-level missing bridge message.

#### Scenario: User opens the translator tool from the launcher
- **WHEN** the user clicks the `Traducir audio` tool card from the launcher
- **THEN** the launcher SHALL remain visible in its current window
- **AND** the translator SHALL open in a separate Electron window instead of replacing the launcher view.
