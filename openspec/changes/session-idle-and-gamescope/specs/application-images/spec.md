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

### Requirement: Session audio defaults

Both application images SHALL route the default ALSA playback and control through PulseAudio using Wolf's supplied session server and sink. Image publication SHALL require actual default-ALSA playback from both amd64 and i386 clients reaching an isolated session sink monitor.

#### Scenario: Game uses default ALSA playback
- **WHEN** a 32-bit or 64-bit application opens the default ALSA PCM with a reachable session Pulse server
- **THEN** its non-silent samples reach the selected session sink without requiring a host ALSA sound card
