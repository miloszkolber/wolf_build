## ADDED Requirements

### Requirement: Steam compositor selection

Both application images SHALL default to Gamescope and SHALL retain an explicit Sway fallback. Steam SHALL enable Gamescope's Steam integration for Big Picture composition.

#### Scenario: Steam requests gamescope
- **WHEN** `RUN_GAMESCOPE` is set on the Steam runner
- **THEN** the session starts gamescope with Wolf's display width, height and refresh and runs the Steam startup under it
- **AND** the guest cursor hides after the same idle delay as the Sway session

#### Scenario: Heroic composition
- **WHEN** Heroic starts with its default environment
- **THEN** it runs through Gamescope without Steam-specific integration

#### Scenario: Default composition
- **WHEN** no compositor variable is set
- **THEN** the application starts under Gamescope

#### Scenario: Explicit fallback
- **WHEN** `RUN_GAMESCOPE` is explicitly empty
- **THEN** the application starts under nested Sway
