# Deferred work

- Consider further rootfs extraction or shell removal only after the supported-base runtime passes integration and dynamic plugin inventories establish what can be removed safely.
- Consider additional Intel architectures only when an actual deployment provides a separate acceptance target.
- Consider further application-image pruning after the Steam/Heroic images pass rendering and game compatibility acceptance. Application and streaming-runtime dependency closures are distinct.
- Review upstream's Fedora-only Wolf image chain only if the independent Ubuntu 26.04 recipes hit a concrete incompatibility. The base choice remains settled otherwise.
- Recheck the pinned shared-gate digest each review: the gate publisher serves only its recent versions, so a pinned consumer digest can disappear from the registry without any gate source change.
- Desktop Shift+Tab overlay investigation and client-disconnection diagnosis remain outside the scope of the [session idle and Gamescope change](changes/archive/2026-11-02-session-idle-and-gamescope/proposal.md), which includes the accepted Big Picture compositor repair.
