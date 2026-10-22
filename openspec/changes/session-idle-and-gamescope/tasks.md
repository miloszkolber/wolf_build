# Tasks

## 1. Idle session stop in the runtime

- [x] 1.1 Add the supervised watcher and its event/transport tests. A paused session arms one deadline, resume and stop clear it, failed stop requests retry a bounded number of times, and a split event stream parses completely.
- [x] 1.2 Verify the watcher against the live Wolf API without stopping anything: subscribe to `/api/v1/events` on the running runtime and confirm the keepalive stream stays connected.
- [ ] 1.3 Build and publish the runtime candidate and confirm the supervised program starts with Wolf in the final image.
- [ ] 1.4 Operator check on the host: a real session resumes inside the grace period, and a client that disappears ends the application container after the timeout, after which gate stops the runtime.
- [ ] 1.5 Remove the temporary host scheduler task once the published runtime is deployed.

## 2. Gamescope for the Steam image

- [x] 2.1 Add gamescope to the Steam package target and resolve its exact closure. The closure adds no audio server, Bluetooth daemon or supervisor.
- [x] 2.2 Honor `RUN_GAMESCOPE` in the shared launcher and fail clearly when the requested compositor is not installed. Sway remains the default.
- [x] 2.3 Extend the final-image check and document the selector and cursor behavior.
- [ ] 2.4 Publish the Steam candidate and confirm the image starts a session under gamescope with Wolf's resolution and refresh.
- [ ] 2.5 Operator check on the TV: Big Picture menu over a running game, game input, audio and controller, then the same checks under Sway for Heroic.

## 3. Repository checks

- [x] 3.1 Unit tests, documentation rules, strict OpenSpec validation and `git diff --check` pass in the development container.
- [ ] 3.2 Review the pushed build and publication run for both images.
