## ADDED Requirements

### Requirement: Public GitHub README
The repository SHALL provide an English public README that introduces the project, shows relevant images, summarizes feature status, links to deeper documentation and avoids exposing local secrets.

#### Scenario: Visitor opens the repository
- **WHEN** a visitor opens the GitHub repository landing page
- **THEN** the README SHALL show the project logo
- **AND** SHALL include a navigable table of contents
- **AND** SHALL summarize current capabilities, platform support, roadmap and limitations in English
- **AND** SHALL link to the repository license

#### Scenario: Visitor reviews visual product direction
- **WHEN** a visitor scans the README
- **THEN** the README SHALL show a screenshot of the desktop translation UI currently being developed

#### Scenario: Visitor checks platform readiness
- **WHEN** a visitor checks supported operating systems
- **THEN** the README SHALL use colored round indicators to distinguish working, experimental and not-yet-implemented support
