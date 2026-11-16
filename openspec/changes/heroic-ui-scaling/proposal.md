# Heroic resolution-aware UI scaling

## Why

Heroic runs in Console Mode under Gamescope at the stream's native resolution. Gamescope presents that resolution but does not scale the launcher UI, so the interface is physically small on a 4K television. The operator requested 200% UI at 4K, 150% at 1440p and 100% at 1080p.

## What changes

- Derive an Electron device scale factor from Wolf's session height in the Heroic launch path.
- Use 200% at 2160 or above, 150% at 1440 or above, and the existing 100% below that.
- Leave the game render resolution, Gamescope output, Moonlight stream size and persistent Heroic configuration unchanged.

## Capabilities and authority

The affected capability is `application-images`. This is a requested launcher UI change. It does not change the streaming runtime, sandbox policy, application downloads or host configuration.
