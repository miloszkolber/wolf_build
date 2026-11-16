## ADDED Requirements

### Requirement: Resolution-aware Heroic UI scale

Heroic SHALL apply an Electron device scale factor derived from Wolf's session height so its launcher interface remains readable on television output. It SHALL use 200% at 2160 or above, 150% at 1440 or above, and 100% below 1440. The scale factor SHALL NOT change game render resolution, the streamed frame size or persistent Heroic configuration.

#### Scenario: 4K session
- **WHEN** Wolf supplies a session height of 2160 or greater
- **THEN** Heroic starts with a 200% device scale factor

#### Scenario: 1440p session
- **WHEN** Wolf supplies a session height of at least 1440 and below 2160
- **THEN** Heroic starts with a 150% device scale factor

#### Scenario: 1080p session
- **WHEN** Wolf supplies a session height below 1440
- **THEN** Heroic starts with its existing 100% scale and no added device-scale flag

#### Scenario: Game playback
- **WHEN** Heroic launches a game
- **THEN** the game keeps the session's render resolution and is not scaled by the launcher's device scale factor
