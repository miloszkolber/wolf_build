#!/bin/bash
# Exercise our session scripts with real headless Sway/Xwayland and a fake app.
# No network, GPU, audio server, Docker socket or production state is supplied.
set -euo pipefail
image=${1:?image tag required}
kind=${2:?steam or heroic required}
case "$kind" in steam|heroic) binary=$kind ;; *) exit 1 ;; esac
probe="wolf-app-probe:$$"
container="wolf-app-probe-$$"
parent="wolf-app-parent-$$"
volume="wolf-app-probe-$$"
parent_volume="wolf-app-parent-$$"
temp=$(mktemp -d)
cleanup() {
    docker rm -f "$container" >/dev/null 2>&1 || true
    docker rm -f "$parent" >/dev/null 2>&1 || true
    docker volume rm "$volume" >/dev/null 2>&1 || true
    docker volume rm "$parent_volume" >/dev/null 2>&1 || true
    docker image rm "$probe" >/dev/null 2>&1 || true
    rm -rf "$temp"
}
trap cleanup EXIT
cat > "$temp/fake-app" <<'APP'
#!/bin/bash
set -euo pipefail
xdpyinfo >/dev/null
test "$PULSE_SERVER" = unix:/run/user/1000/test-pulse
test "$(id -u)" = 1234
test -w "$HOME"
if [ "${SECOND_RUN:-0}" = 1 ]; then test -f "$HOME/persistence-probe"; fi
touch "$HOME/persistence-probe"
if [ "$APP_KIND" = heroic ]; then
    test "$1" = --console
    test "$2" = --fullscreen
else
    test "$(nmcli -g RUNNING general)" = running
fi
echo SESSION_PROBE_PASS
APP
cat > "$temp/Dockerfile" <<'DOCKER'
ARG IMAGE
FROM ${IMAGE}
ARG BINARY
COPY fake-app /tmp/fake-app
COPY parent.conf /tmp/parent.conf
RUN install -m 755 /tmp/fake-app "$(command -v "$BINARY")" && rm /tmp/fake-app
DOCKER
printf 'xwayland disable\n' > "$temp/parent.conf"
docker build --build-arg "IMAGE=$image" --build-arg "BINARY=$binary" -t "$probe" "$temp"
docker volume create "$volume" >/dev/null
for run in 0 1; do
    timeout 45s docker run --rm --name "$container" --network none \
        -v "$volume:/home/retro" -e SECOND_RUN="$run" -e PUID=1234 -e PGID=1235 \
        -e WAYLAND_DISPLAY=unused -e PULSE_SERVER=unix:/run/user/1000/test-pulse \
        -e WLR_BACKENDS=headless -e WLR_RENDERER=pixman "$probe" > "$temp/session.log" 2>&1 || {
        cat "$temp/session.log" >&2; exit 1;
    }
    grep -q '^SESSION_PROBE_PASS$' "$temp/session.log" || { cat "$temp/session.log" >&2; exit 1; }
done
# Reproduce Wolf's restricted root-owned socket handoff with a real compositor.
# The parent needs no GPU. Only its socket is transferred, not a game library.
docker volume create "$parent_volume" >/dev/null
docker run -d --name "$parent" --network none -v "$parent_volume:/parent" \
    -e PUID=1234 -e PGID=1235 -e XDG_RUNTIME_DIR=/parent \
    -e WLR_BACKENDS=headless -e WLR_RENDERER=pixman \
    "$probe" sway --config /tmp/parent.conf >/dev/null
ready=false
for attempt in {1..50}; do
    if docker exec "$parent" test -S /parent/wayland-1; then ready=true; break; fi
    sleep 0.2
done
if [ "$ready" != true ]; then docker logs "$parent" >&2; exit 1; fi
docker exec "$parent" sh -ec 'chown 0:0 /parent/wayland-1; chmod 600 /parent/wayland-1'
timeout 45s docker run --rm --name "$container" --network none \
    -v "$volume:/home/retro" -v "$parent_volume:/parent" \
    -e PUID=1234 -e PGID=1235 -e SECOND_RUN=1 \
    -e WAYLAND_DISPLAY=/parent/wayland-1 -e WLR_BACKENDS=wayland -e WLR_RENDERER=pixman \
    -e PULSE_SERVER=unix:/run/user/1000/test-pulse "$probe" > "$temp/nested.log" 2>&1 || {
    cat "$temp/nested.log" >&2; exit 1;
}
grep -q '^SESSION_PROBE_PASS$' "$temp/nested.log" || { cat "$temp/nested.log" >&2; exit 1; }
echo 'Headless and nested Xwayland, root-owned Wayland socket handoff, non-root identity, persistence and normal shutdown checked; game/GPU/audio acceptance not claimed.'
