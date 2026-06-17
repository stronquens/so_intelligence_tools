## MODIFIED Requirements

### Requirement: Electron overlay launcher view
The desktop application SHALL provide an Electron/Vue overlay launcher view that behaves as a single-instance desktop utility when launched from an OS shortcut.

#### Scenario: Shortcut launch while overlay is already visible
- **WHEN** the overlay is already running and visible
- **AND** the user launches it again through the Windows shortcut
- **THEN** the existing overlay window SHALL be minimized or hidden
- **AND** no additional Electron app instance SHALL remain running.

#### Scenario: Shortcut launch while overlay is minimized or hidden
- **WHEN** the overlay is already running but minimized or hidden
- **AND** the user launches it again through the Windows shortcut
- **THEN** the existing overlay window SHALL be restored, centered, shown and focused
- **AND** no additional Electron app instance SHALL remain running.
