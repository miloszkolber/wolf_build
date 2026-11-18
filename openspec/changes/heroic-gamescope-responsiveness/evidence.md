# Evidence

The initial live inspection found Heroic's Electron GPU and renderer processes under Xwayland. The virtual controller device was present and already opened by Heroic. This proves device visibility and an open descriptor, not successful Chromium Gamepad API enumeration or menu input. The upstream guide and community report motivated a candidate flag change but did not establish the cause of this session's stalls.

The launch-path regression invokes `docker/apps/run.sh` with a `heroic` shim and verifies the complete argument list at 2160, 1440, 1200 and 1080. The expected common arguments are `--console --fullscreen --no-sandbox --ozone-platform=x11 --enable-features=UseOzonePlatform,WaylandWindowDecorations`, followed by the resolution scale where applicable.

The development container ran 87 unit tests, checked 47 Markdown files, passed strict OpenSpec validation for six specifications and both active Heroic changes, and passed shell syntax.

[Application workflow 43940703960](https://github.com/miloszkolber/wolf_build/actions/runs/43940703960) built and published Heroic `4d03d9995009654a` and `latest` at `sha256:4deccdf34d8ee4e5128e84b987ebf42a143c81b3588e3f1447a2514ff3614266`. Its first Heroic publish hit a transient GHCR `unknown blob` failure; the failed publish job was retried and passed. The published launcher produced the expected flag list for a 2160-height session in an isolated image check.

A running Heroic container was not restarted or modified. Real interface responsiveness, gamepad navigation, game launch and Moonlight acceptance remain unverified and are required before archiving this change.

## Failed candidate and reopened diagnosis

The operator reports that severe UI lag and unreliable gamepad detection at launch persist while games remain smooth. Read-only inspection confirms that the active session runs the published candidate digest with both compatibility flags and the 200% launcher scale. Gamescope's focused-window property and X11 `GetInputFocus` identify the Heroic window. Heroic has the virtual controller's event device open. Neither observation establishes renderer-level focus or input processing.

A disposable, network-isolated fixture used the candidate image's bundled Electron and Gamescope, nested under a separate GPU-backed headless Sway compositor with the same resolution, refresh and scaling arguments. It had no production home, game library, input devices or session sockets. Minimal animated Electron, fresh-profile regular Heroic and fresh-profile Console Mode all completed frame-timing probes without reproducing the reported multi-second stalls. This does not test library navigation, real controller detection or the Wolf compositor boundary. Deployment-specific measurements remain outside the repository.

The fixture's first setup attempts failed because a pixman-only parent lacked the required surface support. A GPU-backed Vulkan parent supplied it. The reported libva initialization error also occurred during the responsive fixture runs, so that message alone is not evidence of the stall's cause.

No additional launcher flags or packaged-app patches were applied. A renderer timing, focus and Gamepad API capture during the affected real session is still needed. Restart-dependent instrumentation requires a separately authorized quiet window. The current session and persistent state were not changed.
