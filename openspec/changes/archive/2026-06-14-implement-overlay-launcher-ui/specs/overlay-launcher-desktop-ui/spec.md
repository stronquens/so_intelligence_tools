# overlay-launcher-desktop-ui

## ADDED Requirements

### Requirement: Electron overlay launcher view
The desktop application SHALL provide an Electron/Vue overlay launcher view based on the stored design reference.

#### Scenario: Default desktop view opens the launcher
- **WHEN** the desktop app opens without an explicit alternate view
- **THEN** it SHALL render the overlay launcher as the first screen

#### Scenario: Packaged renderer loads from local files
- **WHEN** Electron loads the built renderer with `loadFile`
- **THEN** the generated HTML SHALL reference JavaScript and CSS assets with relative paths

#### Scenario: Overlay shows primary tools
- **WHEN** the overlay launcher is visible
- **THEN** it SHALL show eight primary tool cards for text correction, OCR, audio translation, translated microphone, dictation, assistant, summary, and intelligent capture

#### Scenario: Overlay window floats above the desktop
- **WHEN** the Electron overlay window is opened
- **THEN** it SHALL use a frameless transparent window
- **AND** it SHALL stay above normal application windows while visible

#### Scenario: Overlay opens centered
- **WHEN** the overlay is shown from a keyboard command or app launch
- **THEN** it SHALL center itself in the active display work area

#### Scenario: Overlay opens settings panel from the settings button
- **WHEN** the overlay launcher is visible
- **AND** the user clicks the settings button
- **THEN** it SHALL show a settings panel with shortcut rows and toggles for startup and always-visible behavior
- **AND** no other tool card SHALL execute a real action in this visual-only iteration

#### Scenario: Existing translator remains reachable
- **WHEN** the desktop URL includes `?view=translator`
- **THEN** the app SHALL render the existing realtime translator UI instead of the launcher
