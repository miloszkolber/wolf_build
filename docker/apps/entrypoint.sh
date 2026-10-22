#!/bin/bash
set -euo pipefail
if [ "$(id -u)" = 0 ]; then
    [[ ${PUID} =~ ^[1-9][0-9]{0,9}$ && ${PGID} =~ ^[1-9][0-9]{0,9}$ ]] || {
        echo 'PUID and PGID must be non-root numeric IDs' >&2; exit 1;
    }
    getent group "$PGID" >/dev/null || groupadd -g "$PGID" "app-$PGID"
    # Do not recursively chown an existing game library when changing identity.
    usermod -d /nonexistent -u "$PUID" -g "$PGID" retro
    usermod -d "$HOME" retro
    mkdir -p "$HOME" "$XDG_RUNTIME_DIR"
    chown "$PUID:$PGID" "$HOME" "$XDG_RUNTIME_DIR"
    chmod 700 "$XDG_RUNTIME_DIR"
    # Wolf runs its compositor as root and bind-mounts this session's socket.
    # Transfer only that socket to the app user before dropping privileges.
    if [ -n "${WAYLAND_DISPLAY:-}" ]; then
        case "$WAYLAND_DISPLAY" in
            /*) wayland_socket=$WAYLAND_DISPLAY ;;
            *) wayland_socket="$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ;;
        esac
        if [ -S "$wayland_socket" ] && [ ! -L "$wayland_socket" ]; then
            chown "$PUID:$PGID" "$wayland_socket"
            chmod u+rw "$wayland_socket"
        fi
    fi
    for device in /dev/dri/* /dev/input/* /dev/hidraw*; do
        [ -c "$device" ] || continue
        gid=$(stat -c %g "$device")
        [ "$gid" != 0 ] || continue
        getent group "$gid" >/dev/null || groupadd -g "$gid" "device-$gid"
        usermod -aG "$(getent group "$gid" | cut -d: -f1)" retro
    done
    # gamescope carries file capabilities; upstream's base hands it to the
    # application user before the session starts it unprivileged.
    if gamescope_bin=$(command -v gamescope); then
        chown "$PUID:$PGID" "$gamescope_bin"
    fi
    if [ "$APP_KIND" = steam ] && [ "${1:-}" = /opt/app/launch.sh ]; then
        # A container-private bus lets Big Picture inspect its own network.
        # Keep Docker's addresses/DNS and deny the status daemon network changes.
        mkdir -p /run/dbus
        dbus-daemon --system --fork --nopidfile
        setpriv --bounding-set=-net_admin,-net_raw -- \
            NetworkManager --no-daemon --config /opt/app/NetworkManager.conf &
        ready=false
        for attempt in {1..50}; do
            if nmcli general status >/dev/null 2>&1; then ready=true; break; fi
            sleep 0.1
        done
        if [ "$ready" != true ]; then echo 'Network status service failed to start' >&2; exit 1; fi
    fi
    exec gosu retro "$@"
fi
exec "$@"
