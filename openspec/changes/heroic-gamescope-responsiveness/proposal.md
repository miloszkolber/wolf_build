# Heroic Gamescope responsiveness

## Why

Heroic's interface is severely sluggish and gamepad navigation is unreliable at launch while games play smoothly. The initial candidate added compatibility flags from Heroic's Gamescope guide, but the operator reports the same failure with the published candidate running. Missing flags are not an established cause. Rendering, frame scheduling and Gamepad API behavior still need direct diagnosis.

## What changes

- Start Heroic with `--ozone-platform=x11` and `--enable-features=UseOzonePlatform,WaylandWindowDecorations`, matching Heroic's gamescope guidance.
- Keep the existing Console Mode, fullscreen, no-sandbox, resolution-derived UI scale and game launch behavior.
- Do not change the running Heroic container. The flags apply on the next Heroic launch.

## Capabilities and authority

The affected capability is `application-images`. This is a requested launcher responsiveness repair. It does not change the streaming runtime, sandbox policy or persistent user state.
