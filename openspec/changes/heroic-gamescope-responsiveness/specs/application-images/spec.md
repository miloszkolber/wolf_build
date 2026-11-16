## ADDED Requirements

### Requirement: Gamescope-compatible Heroic launch

When Heroic runs under Gamescope, the image SHALL start Heroic with the compositor compatibility flags documented by Heroic: X11 Ozone and the Ozone/Wayland-decoration features. It SHALL preserve Console Mode, fullscreen, the configured no-sandbox policy and the resolution-derived UI scale.

#### Scenario: Heroic starts under Gamescope
- **WHEN** Wolf launches Heroic with `RUN_GAMESCOPE` set
- **THEN** Heroic starts with `--ozone-platform=x11` and `--enable-features=UseOzonePlatform,WaylandWindowDecorations`
- **AND** it still receives `--console --fullscreen --no-sandbox` and the height-derived scale flag

#### Scenario: Running session
- **WHEN** an image update adds these flags
- **THEN** an already-running Heroic container is not restarted or modified
- **AND** the flags take effect on the next Heroic launch
