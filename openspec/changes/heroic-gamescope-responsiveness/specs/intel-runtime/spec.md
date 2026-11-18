## ADDED Requirements

### Requirement: Consistent joydev discovery metadata

The runtime SHALL provide private udev database classification for each delivered joystick node so that an application enumerating an already-present controller receives the same classification as a hotplug listener. It SHALL preserve existing supplied records and remove synthesized records when that controller is unplugged.

#### Scenario: Controller precedes application enumeration
- **GIVEN** a controller addition includes a joydev node classified as a joystick
- **WHEN** the runtime delivers that device to the application container
- **THEN** its private udev database includes `ID_INPUT=1` and `ID_INPUT_JOYSTICK=1` for the joydev device's actual major and minor
- **AND** Chromium can enumerate the controller and expose its standard mapped state after controller interaction without requiring a disconnect and reconnect

#### Scenario: Multiple controllers and unplug
- **WHEN** controllers with different joydev minors are added and one is unplugged
- **THEN** each has its own classification record
- **AND** unplug removes only that controller's supplied and synthesized records

#### Scenario: Existing metadata and unrelated devices
- **WHEN** the upstream event already supplies a database record or describes a non-joydev node
- **THEN** the runtime preserves the supplied record and does not invent joystick classification for unrelated nodes
