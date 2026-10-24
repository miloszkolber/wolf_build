#!/bin/bash
set -euo pipefail
# The parent compositor exports its child display to this process.
if [ -z "${RUN_GAMESCOPE:-}" ]; then
    trap 'swaymsg exit >/dev/null 2>&1 || true' EXIT
fi
case "$APP_KIND" in
steam)
    # Match upstream's Steam/Xwayland path, not a native Wayland client.
    if [ -n "${RUN_GAMESCOPE:-}" ]; then unset WAYLAND_DISPLAY; fi
    mkdir -p "$HOME/.steam/ubuntu12_32/steam-runtime"
    # Preserve simple upstream flags/game URLs without evaluating shell code.
    read -r -a flags <<< "${STEAM_STARTUP_FLAGS:--bigpicture}"
    steam "${flags[@]}"
    ;;
heroic)
    # Heroic manages GOG acquisition and its own GE-Proton/UMU runners.
    heroic --console --fullscreen
    ;;
*) echo 'Unsupported application' >&2; exit 1 ;;
esac
