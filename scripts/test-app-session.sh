#!/bin/bash
# Exercise our session scripts with real headless Sway/Xwayland and a fake app.
# No network, GPU, audio server, Docker socket or production state is supplied.
set -euo pipefail
image=${1:?image tag required}
kind=${2:?steam or lutris required}
case "$kind" in steam|lutris) binary=$kind ;; *) exit 1 ;; esac
probe="wolf-app-probe:$$"
container="wolf-app-probe-$$"
volume="wolf-app-probe-$$"
temp=$(mktemp -d)
cleanup() {
    docker rm -f "$container" >/dev/null 2>&1 || true
    docker volume rm "$volume" >/dev/null 2>&1 || true
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
if [ "$APP_KIND" = lutris ]; then
    test "$(readlink "$HOME/.config/lutris/games")" = /var/lutris/library
    test "$(readlink "$HOME/.local/share/lutris")" = /var/lutris/share
fi
echo SESSION_PROBE_PASS
APP
cat > "$temp/Dockerfile" <<'DOCKER'
ARG IMAGE
FROM ${IMAGE}
ARG BINARY
COPY fake-app /tmp/fake-app
RUN install -m 755 /tmp/fake-app "$(command -v "$BINARY")" && rm /tmp/fake-app
DOCKER
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
echo 'Headless Xwayland, socket env, non-root identity, persistence and normal shutdown checked; game/GPU/audio acceptance not claimed.'
