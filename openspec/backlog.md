# Deferred work

- Consider further rootfs extraction or shell removal only after the supported-base runtime passes integration and dynamic plugin inventories establish what can be removed safely.
- Consider additional Intel architectures only when an actual deployment provides a separate acceptance target.
- Consider further application-image pruning after the Steam/Heroic images pass rendering and game compatibility acceptance. Application and streaming-runtime dependency closures are distinct.
- Resume Wolf `stable` tracking and review the upstream release after `games-on-whales/wolf` publishes its first calendar release. The hold, its reviewed identity and the current evidence are in [maintenance-state.md](maintenance-state.md).
- Review upstream's Fedora-only Wolf image chain only if the independent Ubuntu 26.04 recipes hit a concrete incompatibility. The base choice remains settled otherwise.
- Recheck the pinned shared-gate digest each review: the gate publisher serves only its recent versions, so a pinned consumer digest can disappear from the registry without any gate source change.
- Evaluate a GStreamer series change for the runtime. Wolf declares the 1.26 series, whose last release is `1.26.11` (2026-03-10); advisories published from 2026-04-07 through 2026-10-08 name fixes in 1.28.2-1.28.8 only, across core, base, good, bad and ugly components this image builds. A 1.28 adoption needs build, plugin-closure and real-session evidence plus operator authorization because it reselects the graphics/media stack. [maintenance-state.md](maintenance-state.md) records the reviewed advisories and affected components.
- The active [session idle and Gamescope change](changes/session-idle-and-gamescope/proposal.md) owns the Big Picture compositor repair and its pending TV acceptance. Desktop Shift+Tab overlay investigation and client-disconnection diagnosis are outside the requested scope.
