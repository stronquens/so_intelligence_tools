# tools-overlay Delta

## ADDED Requirements

### Requirement: Overlay visual design reference
The overlay SHALL keep `assets/design/overlay-future-reference.jpg` as the visual product reference for future launcher and settings UI work.

#### Scenario: Future overlay work consults the reference
- **WHEN** a new overlay iteration is designed or implemented
- **THEN** the team SHALL consult `assets/design/overlay-future-reference.jpg` as product direction for layout, density, visual tone, launcher actions, and settings affordances

#### Scenario: The reference is not pixel-perfect
- **WHEN** platform-specific constraints require UI differences
- **THEN** the implementation MAY adapt window controls, native behavior, spacing, and accessibility details while preserving the overall product direction
