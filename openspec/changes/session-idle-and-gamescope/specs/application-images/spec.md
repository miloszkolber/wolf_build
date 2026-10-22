## ADDED Requirements

### Requirement: Steam compositor selection

The Steam image SHALL support gamescope as an alternative to nested Sway so the Big Picture menu can appear over a running game, and SHALL fail clearly when a requested compositor is not installed. Sway SHALL remain the default for both application images.

#### Scenario: Steam requests gamescope
- **WHEN** `RUN_GAMESCOPE` is set on the Steam runner
- **THEN** the session starts gamescope with Wolf's display width, height and refresh and runs the Steam startup under it
- **AND** the guest cursor hides after the same idle delay as the Sway session

#### Scenario: Unsupported compositor request
- **WHEN** `RUN_GAMESCOPE` is set for an image that does not carry gamescope, such as Heroic
- **THEN** startup fails with a clear error instead of silently falling back to Sway

#### Scenario: Default composition
- **WHEN** no compositor variable is set
- **THEN** the application starts under nested Sway as before
