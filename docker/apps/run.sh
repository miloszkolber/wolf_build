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
lutris)
    mkdir -p /var/lutris/{Games,library,share} "$HOME/.config/lutris" "$HOME/.local/share"
    for mapping in '.config/lutris/games:library' '.local/share/lutris:share'; do
        target="$HOME/${mapping%%:*}"
        if [ ! -e "$target" ] && [ ! -L "$target" ]; then ln -s "/var/lutris/${mapping##*:}" "$target"; fi
    done
    if [ ! -e "$HOME/.config/lutris/system.yml" ]; then
        printf 'system:\n  game_path: /var/lutris/Games\n' > "$HOME/.config/lutris/system.yml"
    fi
    lutris
    ;;
*) echo 'Unsupported application' >&2; exit 1 ;;
esac
