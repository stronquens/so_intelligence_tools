## MODIFIED Requirements

### Requirement: Electron overlay launcher view
The desktop application SHALL provide an Electron/Vue overlay launcher view based on the stored design reference, and its primary tool cards SHALL open the matching desktop experience when one exists.

#### Scenario: Audio translation card opens new translator view
- **WHEN** the overlay launcher is visible
- **AND** the user clicks `Traducir audio`
- **THEN** the desktop app SHALL open the new Electron/Vue translator view in a separate window
- **AND** the launcher SHALL remain visible
- **AND** it SHALL NOT launch the original Linux translation UI.
