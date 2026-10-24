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

## Executed checks

- Revision `75b66d2`: 68 unit tests, `check-docs.mjs`, pinned strict OpenSpec validation and `git diff --check` passed in the development container. Launcher tests cover Steam `-e`, ordinary Heroic composition and refresh validation. Observer tests reject startup seeding of unknown connection state.
- Hosted application run `40111183659` and runtime run `40111183876` passed build, final-image checks, vulnerability gates and publication.
- The published runtime's synthetic-session probe used `--network none`, temporary state mounts, GPU devices and no Docker socket. With `WOLF_SESSION_IDLE_TIMEOUT=5`, a session created while `supervisorctl stop wolf-session-idle` was in effect survived observer restart beyond five seconds. `POST /api/v1/sessions/pause` then produced a stop within the configured interval, and `GET /api/v1/sessions` returned an empty list.
- Real application launches through Wolf confirmed Gamescope/Xwayland and the actual Steam Big Picture and Heroic processes. Steam logged guide/QAM hotkey bindings with `-e` integration. This is not an assertion of visible TV overlay acceptance.
- Revision `6e992d6`: application run `40111931209` and runtime run `40111931204` passed all required gates. The final Heroic image successfully extracted and selected its downloaded Proton runner and updated vkd3d, rather than merely passing a binary-presence check. Both final app images launched through Wolf. Test sessions stopped cleanly, and the gate's idle shutdown and health-without-wake behavior were checked separately.
- After the host reboot, Ubuntu's AppArmor unprivileged-user-namespace restriction aborted Heroic 2.22.4's Electron zygote (`Failed to move to new namespace`). The pre-reboot image fails identically, so the change is the host policy, not the image. Heroic now starts with `--no-sandbox`; the application container remains the isolation boundary. Application run `40128732987` passed, and the published Heroic and Steam images both launched through Wolf with Gamescope after the change.
