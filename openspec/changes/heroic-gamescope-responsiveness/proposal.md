# Heroic Gamescope responsiveness

## Why

Heroic's interface is severely sluggish and gamepad navigation is unreliable at launch while games play smoothly. The initial candidate added compatibility flags from Heroic's Gamescope guide, but the operator reports the same failure with the published candidate running. Missing flags are not an established cause. Rendering, frame scheduling and Gamepad API behavior still need direct diagnosis.

Controlled Wolf-session tests now reproduce an independent startup gamepad failure. Chromium ignores an already-present joydev node when its private udev database lacks `ID_INPUT_JOYSTICK`, even though the sibling event node is visible and open. Supplying the missing database record makes fresh Chromium enumeration succeed without reconnecting the pad. This does not establish the cause of the reported UI stalls.

## What changes

- Start Heroic with `--ozone-platform=x11` and `--enable-features=UseOzonePlatform,WaylandWindowDecorations`, matching Heroic's gamescope guidance.
- Keep the existing Console Mode, fullscreen, no-sandbox, resolution-derived UI scale and game launch behavior.
- Apply launcher changes on a later launch. Diagnostic restarts and the controller rollout now have an operator-authorized quiet window.
- Complete Wolf's joydev udev database records from its existing hotplug metadata before delivering device additions. Remove the synthesized records on unplug.
- Preserve supplied udev entries, other input devices, controller identity and game behavior.

## Capabilities and authority

The affected capabilities are `application-images` and `intel-runtime`. The operator authorized diagnostic sessions and restarts after finishing gameplay. The controller repair changes only the runtime's private device-metadata handoff. It does not change sandbox policy, pairing or persistent launcher/game settings. Interface responsiveness still requires a separate evidenced repair or real-client diagnosis.
