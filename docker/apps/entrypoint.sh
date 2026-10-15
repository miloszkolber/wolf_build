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
    if [ "${APP_KIND}" = lutris ]; then chown "$PUID:$PGID" /var/lutris; fi
    for device in /dev/dri/* /dev/input/* /dev/hidraw*; do
        [ -c "$device" ] || continue
        gid=$(stat -c %g "$device")
        [ "$gid" != 0 ] || continue
        getent group "$gid" >/dev/null || groupadd -g "$gid" "device-$gid"
        usermod -aG "$(getent group "$gid" | cut -d: -f1)" retro
    done
    exec gosu retro "$@"
fi
exec "$@"
