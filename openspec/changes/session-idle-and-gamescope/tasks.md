# Tasks

## 1. Idle session stop in the runtime

- [x] 1.1 Add the supervised watcher and its event/transport tests. A paused session arms one deadline, resume and stop clear it, failed stop requests retry a bounded number of times, and a split event stream parses completely.
- [x] 1.2 Verify the watcher against the live Wolf API without stopping anything: subscribe to `/api/v1/events` on the running runtime and confirm the keepalive stream stays connected.
- [x] 1.3 Build and publish the runtime candidate and confirm the supervised program starts with Wolf in the final image.
- [x] 1.4 The deployed runtime's watcher was exercised with a synthetic session: a pause armed the deadline, the stop call emptied the session list, and the same code path runs under supervisord with the default 900 s timeout.
- [ ] 1.5 Operator check on the host: a real Moonlight session resumes inside the grace period, and a client that disappears ends the application container after the timeout, after which gate stops the runtime.
- [x] 1.6 Remove the temporary host scheduler task once the published runtime is deployed; the cron entry, script and state file are gone.

## 2. Gamescope for the Steam image

- [x] 2.1 Add gamescope to the Steam package target and resolve its exact closure. The closure adds no audio server, Bluetooth daemon or supervisor.
- [x] 2.2 Honor `RUN_GAMESCOPE` in the shared launcher and fail clearly when the requested compositor is not installed. Sway remains the default.
- [x] 2.3 Extend the final-image check and document the selector and cursor behavior.
- [x] 2.4 Publish the Steam candidate and confirm gamescope initializes in the final image on the Intel GPU under a parent Wayland display at 1920x1080@60.
- [ ] 2.5 Operator check on the TV from Wolf: Big Picture menu over a running game, game input, audio and controller, then the same checks under Sway for Heroic.

## 3. Repository checks

- [x] 3.1 Unit tests, documentation rules, strict OpenSpec validation and `git diff --check` pass in the development container.
- [x] 3.2 Review the pushed build and publication runs for both images, including the reused closures, SBOM/vulnerability results and published digests.
