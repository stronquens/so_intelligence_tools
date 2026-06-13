# Delta Spec

## ADDED Requirements

### Requirement: Windows adapters for text-focused runner flows
The system SHALL provide an initial Windows adapter layer for text-focused Python tool runners without changing the shared application use cases.

#### Scenario: A text tool runs on Windows
- **WHEN** the selected text correction runner is invoked on Windows
- **THEN** the system SHALL compose Windows adapters for clipboard, keyboard automation, selected text, text insertion and notifications
- **AND** the correction use case SHALL remain independent of the concrete operating system.

#### Scenario: Windows selected text is read through a clipboard roundtrip
- **WHEN** a Windows text adapter needs to read selected text from the focused application
- **THEN** it SHALL preserve the existing clipboard when possible
- **AND** it SHALL send a copy shortcut to request the current selection
- **AND** it SHALL return no selection if the clipboard does not change to useful text.

#### Scenario: Windows corrected text is inserted into the focused application
- **WHEN** a Windows text adapter needs to replace selected text
- **THEN** it SHALL write the replacement text to the clipboard
- **AND** it SHALL send a paste shortcut to the focused application.

### Requirement: Platform-aware runtime composition
The system SHALL centralize operating-system runtime selection instead of hardcoding Linux in text-focused entrypoints.

#### Scenario: The runtime is built automatically
- **WHEN** a text-focused runner builds its desktop runtime without an explicit platform
- **THEN** the system SHALL choose a Windows runtime on Windows
- **AND** it SHALL choose the existing Linux runtime on Linux.

#### Scenario: A platform is unsupported
- **WHEN** runtime composition is requested for an unsupported platform
- **THEN** the system SHALL fail with clear unsupported-environment feedback.
