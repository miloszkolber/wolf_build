# Heroic Gamescope responsiveness

## Why

Heroic's interface becomes slow and input feels unreliable under Gamescope when Electron starts without the compositor compatibility flags documented by Heroic. The live Wolf session showed the expected Electron Xwayland process but not the `UseOzonePlatform`/Wayland-decoration feature flags.

## What changes

- Start Heroic with `--ozone-platform=x11` and `--enable-features=UseOzonePlatform,WaylandWindowDecorations`, matching Heroic's gamescope guidance.
- Keep the existing Console Mode, fullscreen, no-sandbox, resolution-derived UI scale and game launch behavior.
- Do not change the running Heroic container. The flags apply on the next Heroic launch.

## Capabilities and authority

The affected capability is `application-images`. This is a requested launcher responsiveness repair. It does not change the streaming runtime, sandbox policy or persistent user state.
