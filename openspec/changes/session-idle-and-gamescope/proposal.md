# Session idle stop and gamescope for the Steam image

## Why

Wolf keeps a paused session and its application container when the Moonlight control channel drops so a short interruption resumes the same game. Nothing in Wolf distinguishes a switched-off TV from a client that is about to return, so a session can run for hours with no client. The shared gate only manages the runtime: it cannot see the streaming client once Wolf owns the ports. The session rule belongs beside Wolf.

The Steam image also lost the Big Picture menu over a running game when it moved from the earlier gamescope configuration to nested Sway. The menu is a surface inside the Steam window, and Sway hides that window behind a fullscreen game and ignores the client's own focus requests. Steam should be able to select gamescope again.

## What changes

- Add a supervised watcher beside Wolf in the runtime image. It follows Wolf's event stream, arms a deadline when a session pauses, clears it on resume or stop, and calls Wolf's session stop endpoint after `WOLF_SESSION_IDLE_TIMEOUT` seconds. A value of `0` disables it. The watcher seeds sessions restored at runtime start so a paused session cannot be resurrected without a client, and clears deadlines when its event stream is interrupted rather than stopping on incomplete information.
- Add gamescope to the Steam target and honor `RUN_GAMESCOPE` in the shared launcher. Sway stays the default for both applications; Heroic rejects the request because it does not install gamescope.
- Document the timeout and the compositor choice in the consuming examples.

## Capabilities

Modified capabilities are `intel-runtime` and `application-images`.

## Status and authority

Implementation and repository checks are authorized. Publication is not deployment. The published runtime replaced the host's temporary scheduler task after the supervised watcher started in the deployed container. The on-TV gamescope acceptance and a real Moonlight idle-stop check remain with the operator.

## Dependencies and consequential unknowns

The watcher depends on Wolf's Unix-socket API (`/api/v1/events`, `/api/v1/sessions`, `/api/v1/sessions/stop`) in the pinned source. A future upstream change to those paths or event names must fail visibly rather than silently disable the stop. Gamescope availability, its version, and the overlay result are established by the image build and the operator's TV test, not by these documents.
