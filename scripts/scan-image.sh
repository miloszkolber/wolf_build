#!/bin/bash
# Refresh once, then share the DB and analysis cache between both reports.
set -euo pipefail
archive=${1:-candidate.tar}
test -s "$archive"
cache=$(mktemp -d)
trap 'rm -rf "$cache"' EXIT
trivy() {
    docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
        -v "$PWD:/work" -v "$cache:/cache" aquasec/trivy:0.76.0 --cache-dir /cache "$@"
}
ready=false
for attempt in 1 2 3; do
    if trivy image --download-db-only; then ready=true; break; fi
    if [ "$attempt" != 3 ]; then sleep "$((attempt * 5))"; fi
done
if [ "$ready" != true ]; then echo 'Vulnerability database refresh failed' >&2; exit 1; fi
trivy image --skip-db-update --input "/work/$archive" --format cyclonedx --output /work/candidate.cdx.json
trivy image --skip-db-update --input "/work/$archive" --severity HIGH,CRITICAL --exit-code 1 --format json --output /work/vulnerabilities.json
