# Evidence

The live inspection found Heroic's Electron GPU and renderer processes under Xwayland, with the game using most of the active CPU. The virtual controller device was present and already opened by Heroic, so the device layer was not missing. Heroic's own gamescope guide and the Wolf community report identify the missing `UseOzonePlatform`/Wayland-decoration features as the cause of the launcher stall; the exact Gamepad API behavior still needs a real navigation test.

The launch-path regression invokes `docker/apps/run.sh` with a `heroic` shim and verifies the complete argument list at 2160, 1440, 1200 and 1080. The expected common arguments are `--console --fullscreen --no-sandbox --ozone-platform=x11 --enable-features=UseOzonePlatform,WaylandWindowDecorations`, followed by the resolution scale where applicable.

The development container ran 87 unit tests, checked 47 Markdown files, passed strict OpenSpec validation for six specifications and both active Heroic changes, and passed shell syntax.

[Application workflow 43940703960](https://github.com/miloszkolber/wolf_build/actions/runs/43940703960) built and published Heroic `4d03d9995009654a` and `latest` at `sha256:4deccdf34d8ee4e5128e84b987ebf42a143c81b3588e3f1447a2514ff3614266`. Its first Heroic publish hit a transient GHCR `unknown blob` failure; the failed publish job was retried and passed. The published launcher produced the expected flag list for a 2160-height session in an isolated image check.

A running Heroic container was not restarted or modified. Real interface responsiveness, gamepad navigation, game launch and Moonlight acceptance remain unverified and are required before archiving this change.
