# Deferred work

- Consider further rootfs extraction or shell removal only after the supported-base runtime passes integration and dynamic plugin inventories establish what can be removed safely.
- Consider additional Intel architectures only when an actual deployment provides a separate acceptance target.
- Consider further application-image pruning after the Steam/Heroic images pass rendering and game compatibility acceptance. Application and streaming-runtime dependency closures are distinct.
- Resume Wolf `stable` tracking and review the upstream release after `games-on-whales/wolf` publishes its first calendar release. The hold, its reviewed identity and the current evidence are in [maintenance-state.md](maintenance-state.md).
- Review upstream's Fedora-only Wolf image chain only if the independent Ubuntu 26.04 recipes hit a concrete incompatibility. The base choice remains settled otherwise.
- Recheck the pinned shared-gate digest each review: the gate publisher serves only its recent versions, so a pinned consumer digest can disappear from the registry without any gate source change.
