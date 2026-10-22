#!/bin/bash
set -euo pipefail
: "${WAYLAND_DISPLAY:?Wolf must supply its Wayland display}"
: "${PULSE_SERVER:?Wolf must supply its PulseAudio socket}"
width=${GAMESCOPE_WIDTH:-1920}; height=${GAMESCOPE_HEIGHT:-1080}
[[ $width =~ ^[0-9]+$ && $height =~ ^[0-9]+$ ]] || exit 1

if [ -n "${RUN_GAMESCOPE:-}" ]; then
    # Steam's Big Picture menu is a surface inside the Steam window. A tiling
    # compositor hides that window behind a fullscreen game, while gamescope
    # composites Steam and the game in one session. Steam carries gamescope;
    # other applications reject the request instead of silently using Sway.
    command -v gamescope >/dev/null || { echo 'gamescope requested but not installed' >&2; exit 1; }
    export XDG_CURRENT_DESKTOP=gamescope XDG_SESSION_TYPE=wayland
    exec dbus-run-session -- gamescope -b -W "$width" -H "$height" -r "${GAMESCOPE_REFRESH:-60}" -C 3000 -- /opt/app/run.sh
fi

export SWAYSOCK="$XDG_RUNTIME_DIR/app-sway.sock"
config=$(mktemp "$XDG_RUNTIME_DIR/sway.XXXXXX")
trap 'rm -f "$config"' EXIT
cat > "$config" <<'SWAY'
xwayland enable
default_border none
default_floating_border none
output * bg #000000 solid_color
for_window [class="steam"] fullscreen disabled
for_window [class="steam_app_.*"] fullscreen enabled
bindsym Alt+F4 kill
seat * hide_cursor 3000
seat * hide_cursor when-typing enable
exec /opt/app/run.sh
SWAY
printf 'output * resolution %sx%s\n' "$width" "$height" >> "$config"
# Nested Sway supplies Xwayland to games, not a second host compositor.
export XDG_CURRENT_DESKTOP=sway XDG_SESSION_TYPE=wayland
dbus-run-session -- sway --config "$config"
