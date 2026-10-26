#!/bin/bash
# Exercise real embedded Pulse + supervisor, substituting only GPU-bound Wolf.
set -euo pipefail
image=${1:?runtime image required}
name="wolf-supervision-test-$$"
temp=$(mktemp -d)
cleanup() { docker rm -f "$name" >/dev/null 2>&1 || true; rm -rf "$temp"; }
trap cleanup EXIT
cat > "$temp/wolf" <<'PY'
#!/usr/bin/python3
import signal
import sys
def stop(signum, frame):
    print("WOLF_GRACEFUL_STOP", flush=True)
    sys.exit(0)
signal.signal(signal.SIGINT, stop)
print("WOLF_STARTED", flush=True)
while True:
    signal.pause()
PY
chmod 755 "$temp/wolf"
for scenario in normal pulse-exit; do
    docker run -d --name "$name" --network none --tmpfs /etc/wolf --tmpfs /run/user/wolf --tmpfs /tmp \
        -v "$temp/wolf:/wolf/wolf:ro" "$image" >/dev/null
    ready=false
    for attempt in {1..75}; do
        if docker exec "$name" supervisorctl -c /etc/supervisord.conf status wolf 2>/dev/null | grep -q RUNNING; then ready=true; break; fi
        sleep 0.2
    done
    if [ "$ready" != true ]; then docker logs "$name"; exit 1; fi
    if [ "$scenario" = normal ]; then
        docker stop --time 40 "$name" >/dev/null
    else
        pid=$(docker exec "$name" supervisorctl -c /etc/supervisord.conf pid pulseaudio)
        docker exec "$name" sh -c 'kill -KILL "$1"' sh "$pid"
    fi
    code=$(timeout 45s docker wait "$name")
    test "$code" = 0
    docker logs "$name" > "$temp/log" 2>&1
    grep -q WOLF_GRACEFUL_STOP "$temp/log"
    if [ "$scenario" = pulse-exit ]; then
        grep -q '\[audio-failure\] embedded Pulse exited' "$temp/log"
        test "$(grep -c "spawned: 'pulseaudio'" "$temp/log")" = 1
    else
        if grep -q '\[audio-failure\]' "$temp/log"; then cat "$temp/log"; exit 1; fi
    fi
    docker rm "$name" >/dev/null
    echo "Runtime supervisor $scenario: PASS (Wolf graceful teardown)"
done
