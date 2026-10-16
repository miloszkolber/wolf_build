#!/bin/bash
set -euo pipefail
: "${WAYLAND_DISPLAY:?Wolf must supply its Wayland display}"
: "${PULSE_SERVER:?Wolf must supply its PulseAudio socket}"
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
width=${GAMESCOPE_WIDTH:-1920}; height=${GAMESCOPE_HEIGHT:-1080}
[[ $width =~ ^[0-9]+$ && $height =~ ^[0-9]+$ ]] || exit 1
printf 'output * resolution %sx%s\n' "$width" "$height" >> "$config"
# Nested Sway supplies Xwayland to games, not a second host compositor.
export XDG_CURRENT_DESKTOP=sway XDG_SESSION_TYPE=wayland
dbus-run-session -- sway --config "$config"
