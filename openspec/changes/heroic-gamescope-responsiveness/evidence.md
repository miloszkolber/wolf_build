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

## Authorized diagnosis and startup-controller cause

After the operator authorized tests outside gameplay, the stopped launcher profile was backed up and controlled sessions were created through Wolf's local API with the existing client settings. No pairing records or game files were changed. A loopback-only Node inspector in the application container allowed renderer timing, focus, Gamepad API and input observation without a patched Heroic package.

The populated regular library and Console Mode completed frame-timing probes under the real Wolf compositor without reproducing the reported multi-second stalls. The renderer reported Intel hardware WebGL rather than software fallback. A temporary alternating-color overlay was sent through Wolf's actual H.264 encoder and local UDP output, reconstructed and decoded in the development container. Its visible changes did not reproduce the multi-second delay. The overlay was removed after the test. These are controlled API/input and loopback-transport tests, not TV-client or game acceptance.

The controller failure was reproduced independently. Creating the virtual pad before Chromium initialized left `navigator.getGamepads()` empty despite held D-pad or face-button input, foreground focus and an open event-device descriptor. A separate read confirmed the kernel delivered the input events. Reconnecting the same virtual controller made Chromium open its joydev node and expose a standard mapped gamepad.

Wolf's private udev database contained the event-node classification but no corresponding joydev classification. Chromium's `UdevGamepadLinux::Create` ignores input nodes without `ID_INPUT_JOYSTICK`, and its Linux fetcher reads standard controller state through joydev. An isolated fresh Electron process under the same running compositor and controller reproduced empty enumeration without the joydev database record. Adding only the missing joydev record before another fresh Electron process made enumeration and the same D-pad input succeed. The temporary record was then removed.

The runtime repair completes missing joydev records from Wolf's existing classified hotplug events before device delivery. The same transformation identifies records for removal on unplug. It preserves upstream-supplied entries and ignores unrelated or malformed nodes. It is guarded against the exact pinned runner source and participates in runtime input identity.

The development container ran 88 unit tests, including the compiled C++ metadata helper regression with warnings treated as errors. The regression covers startup records, multiple controllers, duplicate additions, preservation, invalid input and matching unplug cleanup. Applying the patch to the pinned upstream runner source passed. Documentation checks passed for 49 Markdown files, and strict OpenSpec validation passed for all seven items. Final-runtime compilation, publication and rollout are still pending. UI-stall diagnosis remains separate and unresolved.
