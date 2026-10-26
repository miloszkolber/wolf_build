#!/bin/bash
# Real default-ALSA clients (both ABIs) -> isolated session sink -> raw monitor.
set -euo pipefail
image=${1:?application image required}
root=$(cd "$(dirname "$0")/.." && pwd)
name="wolf-audio-test-$$"
server_image="$name-server"
client_image="$name-client"
cleanup() {
    docker rm -f "$name" >/dev/null 2>&1 || true
    docker volume rm "$name" >/dev/null 2>&1 || true
    docker image rm "$server_image" "$client_image" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker build --build-arg "IMAGE=$image" --target audio-server -t "$server_image" "$root/tests/audio"
docker build --build-arg "IMAGE=$image" --target audio-client -t "$client_image" "$root/tests/audio"
docker volume create "$name" >/dev/null
docker run --rm --network none -v "$name:/audio" --entrypoint sh "$server_image" -c 'chown 1000:1000 /audio'
docker run -d --name "$name" --network none --read-only --user 1000:1000 \
    --tmpfs /tmp:mode=1777 -e HOME=/tmp -e XDG_RUNTIME_DIR=/tmp/runtime \
    -e PULSE_SERVER=/audio/pulse -v "$name:/audio" "$server_image" >/dev/null
ready=false
for attempt in {1..50}; do
    if docker exec "$name" pactl info >/dev/null 2>&1; then ready=true; break; fi
    sleep 0.2
done
if [ "$ready" != true ]; then docker logs "$name"; exit 1; fi
# A wrong/default route must not satisfy this check by accident.
docker exec "$name" pactl set-default-sink decoy
for abi in 64 32; do
    docker exec -d "$name" sh -c 'echo $$ >/tmp/recorder.pid; exec parec --device=session-test.monitor --rate=48000 --channels=2 --format=s16le >/audio/capture.raw'
    ready=false
    for attempt in {1..50}; do
        if [ -n "$(docker exec "$name" pactl list short source-outputs)" ]; then ready=true; break; fi
        sleep 0.1
    done
    if [ "$ready" != true ]; then exit 1; fi
    timeout 20s docker run --rm --network none --read-only --user 1000:1000 \
        -e PULSE_SERVER=/audio/pulse -e PULSE_SINK=session-test \
        -v "$name:/audio:ro" --entrypoint "/audio-test/play$abi" "$client_image"
    docker exec "$name" sh -c 'kill "$(cat /tmp/recorder.pid)"'
    docker exec "$name" python3 -c 'import array; s=array.array("h",open("/audio/capture.raw","rb").read()); assert sum(abs(v)>1000 for v in s)>48000, "no sustained audio reached session monitor"'
    echo "${abi}-bit default ALSA -> session Pulse monitor: PASS"
done
