## ADDED Requirements

### Requirement: Dictation shortcut default migration
The desktop settings layer SHALL migrate known legacy push-to-talk dictation defaults to the current project default.

#### Scenario: Legacy dictation shortcut is loaded
- **WHEN** persisted desktop settings contain a known legacy dictation shortcut such as `Ctrl + Space`, `Ctrl + Shift + D`, or `Ctrl + Alt + Space`
- **THEN** the desktop settings layer SHALL replace it with `Ctrl + Shift + Space`.
