#!/bin/bash
set -euo pipefail
# Sway exports the nested DISPLAY and WAYLAND_DISPLAY to this process.
trap 'swaymsg exit >/dev/null 2>&1 || true' EXIT
case "$APP_KIND" in
steam)
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
