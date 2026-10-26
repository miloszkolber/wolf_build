# Tasks

## 1. Idle session stop in the runtime

- [x] 1.1 Add the supervised watcher and its event/transport tests. A paused session arms one deadline, resume and stop clear it, failed stop requests retry a bounded number of times, and a split event stream parses completely.
- [x] 1.2 Verify the watcher against the live Wolf API without stopping anything: subscribe to `/api/v1/events` on the running runtime and confirm the keepalive stream stays connected.
- [x] 1.3 Build and publish the runtime candidate and confirm the supervised program starts with Wolf in the final image.
- [x] 1.4 The deployed runtime's watcher was exercised with a synthetic session: a pause armed the deadline, the stop call emptied the session list, and the same code path runs under supervisord with the default 900 s timeout.
- [ ] 1.5 Operator check on the host: a real Moonlight session resumes inside the grace period, and a client that disappears ends the application container after the timeout, after which gate stops the runtime.
- [x] 1.6 Remove the temporary host scheduler task once the published runtime is deployed; the cron entry, script and state file are gone.

## 2. Gamescope for the Steam image

- [x] 2.1 Add Gamescope to the shared application package target for Steam and Heroic. Keep audio servers outside the application images.
- [x] 2.2 Default both application images to Gamescope, enable Steam integration only for Steam, and retain explicit empty `RUN_GAMESCOPE=` for Sway fallback.
- [x] 2.3 Extend the final-image check and document the selector and cursor behavior.
- [x] 2.4 Publish the Steam candidate and confirm gamescope initializes in the final image on the Intel GPU under a parent Wayland display at 1920x1080@60.
- [ ] 2.5 Operator check on the TV from Wolf: Steam Big Picture menu over a running game, game input, audio and controller, then game/session checks for Heroic under Gamescope.

## 3. Repository checks

- [x] 3.1 Unit tests, documentation rules, strict OpenSpec validation and `git diff --check` pass in the development container.
- [x] 3.2 Review the pushed build and publication runs for both images, including the reused closures, SBOM/vulnerability results and published digests.

## 4. Deployment review

- [x] 4.1 Review the earlier implementation against upstream launch and API contracts. Repair missing Gamescope `-e` Steam integration and unsafe observer startup seeding of connected sessions. Use monotonic deadlines and close failed subscription sockets.
- [x] 4.2 Run 68 unit tests and strict documentation/OpenSpec validation in the development container. Launcher tests check Steam integration, Heroic composition and invalid refresh rejection. Observer tests reject startup assumptions about existing sessions.
- [x] 4.3 Publish and deploy the repaired runtime and both Gamescope application images. Hosted runs `40111183659`, `40111183876`, `40111931209` and `40111931204` passed. Both actual apps launched through Wolf with Gamescope. The isolated runtime preserved a pre-existing session across observer startup and expired it after an observed pause. Unit tests cover resume cancellation and CI checks explicit Sway fallback. Real Moonlight acceptance remains separate.
- [x] 4.4 Remove superseded local images, diagnostic dumps, scratch artifacts and unused launcher remnants. Preserve pairing, launcher state, libraries and saves. Deployment-specific inventory and checks belong to the deployment runbook.

## 5. Game audio and deployment repairs

- [x] 5.1 Route the shared application images' default ALSA PCM/control to the session Pulse server. Verify real 32-bit and 64-bit playback reaches a session sink monitor, and make the check a publication prerequisite.
- [x] 5.2 Retain Pulse diagnostics, require a responsive audio server for runtime health and shut down the runtime coherently when embedded Pulse exits. Verify the actual supervisor failure path without production state or GPU access.
- [x] 5.3 Correct the DRM example and document startup versus live-reset guarantees. Repair saved application hidraw fallback rules using the current kernel major without changing controller selection or persistent game settings. Confirm the pinned runner already injects live majors at creation rather than claiming the stale fallback proves an effective permission failure.
- [x] 5.4 Run repository checks, publish checked images and apply an authorized idle rollout. Record image checks separately from affected-game and audible Moonlight acceptance.

## 6. Repository reliability and build efficiency

- [x] 6.1 Retry individual stop-request transport errors without clearing paused sessions or reconnecting a healthy event stream. Preserve fail-open handling of actual subscription gaps.
- [x] 6.2 Canonicalize submodule identity to path/full-commit pairs and verify tag-only metadata changes cannot change the identity.
- [x] 6.3 Strip the installed VA driver before final image assembly and use component-specific source COPY boundaries. Verify the final stripped candidate's plugins and supported Intel codecs.
- [x] 6.4 Share one freshly updated scanner database between checks with bounded download retries, and let each application publish independently while preserving separate build/publish permissions.
- [x] 6.5 Bound transient upstream requests and Git acquisition, run repository checks, publish checked images and apply an authorized idle rollout without changing the session grace or game state.
