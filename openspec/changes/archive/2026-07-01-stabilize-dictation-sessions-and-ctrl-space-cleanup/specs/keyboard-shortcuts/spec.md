## ADDED Requirements

### Requirement: Old Ctrl Space cleanup is best effort
The Linux installer SHALL treat old `Ctrl + Space` desktop conflicts as best-effort cleanup and SHALL NOT depend on keyboard event suppression.

#### Scenario: Linux desktop integration is installed
- **WHEN** known gsettings keys contain old `Ctrl + Space` bindings
- **THEN** the installer SHALL remove those values where possible
- **AND** it SHALL continue when a schema or key is unavailable.

#### Scenario: Ulauncher owns Ctrl Space
- **WHEN** Ulauncher settings contain `Ctrl + Space` as the app hotkey
- **THEN** the installer SHALL clear that hotkey so Ulauncher no longer opens over dictation.
