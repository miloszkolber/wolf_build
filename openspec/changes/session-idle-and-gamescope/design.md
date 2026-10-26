# Review and delivery

## Review findings

- The first Gamescope launch used generic composition for Steam. Upstream's Steam launcher passes `-e`, unlike its generic app launcher. The maintained launcher now enables that flag only for Steam and unsets the child's `WAYLAND_DISPLAY` for Steam's Xwayland path.
- The observer seeded every existing session when Wolf was younger than 60 seconds. The session-list response carries no connected/paused state, so an already-connected session whose resume occurred before subscription could be stopped after 15 minutes. Seeding is removed. Observed session creation or pause arms a deadline, and resume or stop cancels it.
- The observer intentionally fails open across subscription gaps. Without an authoritative connection-state query it cannot recover a missed pause safely. This trades possibly retained idle sessions during an observer failure for protecting an active game. No claim of persistent session restoration or complete reconciliation is made.
- Failed subscription sockets were not closed. Failed connects and subscription handshakes now close their descriptors. Idle deadlines use a monotonic clock rather than wall time.
- A real Heroic launch exposed a missing decompressor: its downloaded Proton runner failed with `tar (child): xz: Cannot exec: No such file or directory`. The Heroic target now includes `xz-utils` and checks for `xz` in the final-image gate. Empty directories left by the failed extraction are removable artifacts, not installed runners.

## Application composition

Both images carry Gamescope in their shared layer and default to `RUN_GAMESCOPE=1`. Steam uses `-e` for Steam-specific focus and overlay composition. Heroic uses ordinary composition. An explicitly empty `RUN_GAMESCOPE=` selects Sway for rollback and device-free CI smoke tests. Runtime sockets, user homes, input devices and libraries remain unchanged.

## Acceptance boundary

Unit checks and hosted builds cover launcher argument construction, session event framing, idle deadlines, payloads and the explicit Sway fallback. A device-backed Gamescope launch establishes compositor startup and application display wiring, not guide-menu reliability or game compatibility. Steam Big Picture overlay, Heroic games, audio and controllers still require operator TV acceptance.

The repaired runtime was also exercised without production state or Docker authority: stop the observer, create a synthetic session, restart the observer and confirm the unknown existing session survives beyond the short test timeout. Then pause the session and confirm the observer stops it through the API. This reproduces the unsafe startup condition rather than merely asserting a mocked deadline.

## Operator feedback

- 2026-10-24: the Steam Big Picture menu over a running game works flawlessly with Gamescope. This closes the compositor reason for the change; game input, Heroic gameplay, audio and a real idle expiry remain separate checks.
- EMSS audio still crackles or stutters on the TV client. The runtime audio pipeline logged no underruns or read errors, and the client's WebAudio backend works. Treat EMSS as a Tizen-client backend concern; no runtime audio change is justified by this evidence.
- The runtime observed after testing was the operator's live TV session, not a leftover: the gate stopped it after the test runs, then the TV connected and resumed the session. A client that remains connected while its screen is off cannot be distinguished server-side; only a control disconnect starts the idle timer, and a reconnect clears it.

## Game-audio review follow-up

The application images installed both Pulse plugin ABIs but left the ALSA default override as an inactive example. A final-image probe reproduced default PCM failure while explicit Pulse PCM succeeded against the same isolated server. The shared image now supplies `/etc/asound.conf`. Publication checks both real client ABIs against a private session sink and verifies non-silent monitor samples, without installing development packages into the client under test.

Embedded Pulse recovery uses coordinated runtime shutdown, not a second independent restart. Pulse exit destroys virtual sinks and the pinned Wolf context does not rebuild its routing subscription. Supervisor therefore retains diagnostics and sends Wolf its normal stop signal before ending the runtime. This intentionally sacrifices game continuity on a server crash rather than leaving a healthy-looking broken runtime. External Pulse servers remain externally owned. Health queries their availability but does not shut down or restart them.

The deployment example maps the DRM directory and recommends selecting a by-path render identity. It does not promise live GPU-reset recovery or enable a disabled GPU. Per-runner hidraw grants must use the current kernel major independently of the outer runtime's grants.

## Executed checks

- Audio follow-up: 72 unit tests passed. Disposable overlay images based on the previously deployed Steam/runtime artifacts verified the source repair before publication. `scripts/test-app-audio.sh` checked real default ALSA PCM/control from both ABIs against a selected session sink distinct from the server default and found sustained non-silent monitor samples. The same check rejected the pre-fix Steam image with missing hardware card zero. `scripts/test-runtime-supervision.sh` checked actual startup/supervisor configuration with only the GPU-bound Wolf executable substituted: normal shutdown and killed embedded Pulse both gave Wolf its graceful stop signal, and Pulse was not independently restarted. These probes are not canonical image publication or audible game acceptance.

- Revision `75b66d2`: 68 unit tests, `check-docs.mjs`, pinned strict OpenSpec validation and `git diff --check` passed in the development container. Launcher tests cover Steam `-e`, ordinary Heroic composition and refresh validation. Observer tests reject startup seeding of unknown connection state.
- Hosted application run `40111183659` and runtime run `40111183876` passed build, final-image checks, vulnerability gates and publication.
- The published runtime's synthetic-session probe used `--network none`, temporary state mounts, GPU devices and no Docker socket. With `WOLF_SESSION_IDLE_TIMEOUT=5`, a session created while `supervisorctl stop wolf-session-idle` was in effect survived observer restart beyond five seconds. `POST /api/v1/sessions/pause` then produced a stop within the configured interval, and `GET /api/v1/sessions` returned an empty list.
- Real application launches through Wolf confirmed Gamescope/Xwayland and the actual Steam Big Picture and Heroic processes. Steam logged guide/QAM hotkey bindings with `-e` integration. This is not an assertion of visible TV overlay acceptance.
- Revision `6e992d6`: application run `40111931209` and runtime run `40111931204` passed all required gates. The final Heroic image successfully extracted and selected its downloaded Proton runner and updated vkd3d, rather than merely passing a binary-presence check. Both final app images launched through Wolf. Test sessions stopped cleanly, and the gate's idle shutdown and health-without-wake behavior were checked separately.
- After the host reboot, Ubuntu's AppArmor unprivileged-user-namespace restriction aborted Heroic 2.22.4's Electron zygote (`Failed to move to new namespace`). The pre-reboot image fails identically, so the change is the host policy, not the image. Heroic now starts with `--no-sandbox`; the application container remains the isolation boundary. Application run `40128732987` passed, and the published Heroic and Steam images both launched through Wolf with Gamescope after the change.
