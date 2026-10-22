# Deferred work

- Consider further rootfs extraction or shell removal only after the supported-base runtime passes integration and dynamic plugin inventories establish what can be removed safely.
- Consider additional Intel architectures only when an actual deployment provides a separate acceptance target.
- Consider further application-image pruning after the Steam/Heroic images pass rendering and game compatibility acceptance. Application and streaming-runtime dependency closures are distinct.
- Resume Wolf `stable` tracking and review the upstream release after `games-on-whales/wolf` publishes its first calendar release. The hold, its reviewed identity and the current evidence are in [maintenance-state.md](maintenance-state.md).
- Review upstream's Fedora-only Wolf image chain only if the independent Ubuntu 26.04 recipes hit a concrete incompatibility. The base choice remains settled otherwise.
- Recheck the pinned shared-gate digest each review: the gate publisher serves only its recent versions, so a pinned consumer digest can disappear from the registry without any gate source change.
- Steam's guide menu over a running game: the game is a Sway-fullscreen window, so the Big Picture window and the Steam surfaces sharing its workspace stay hidden. Sway also ignored X11 focus and `_NET_ACTIVE_WINDOW` requests addressed to the Steam window, including with `focus_on_window_activation focus`, so Steam cannot raise its own menu above the game. Resolve only through an operator-accepted change to the nested compositor setup or an explicit Sway-side trigger, then verify on the TV.
- Steam's in-game overlay reliability is separate: the overlay renderer view exists at full game size and all overlay libraries resolve, but Proton can report the overlay active with game input disabled while Xwayland logs `failed to create drawable`. Establish the trigger with a debug-level session on the target game before changing the image.
