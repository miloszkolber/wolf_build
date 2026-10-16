#!/bin/bash
# Host Docker orchestration. Pure parsing/final identity runs separately in Python.
set -euo pipefail
cd "$(dirname "$0")/.."
profile=${1:?runtime, steam or heroic}
case "$profile" in
    runtime)
        manifest=.build/manifest.json
        base=$(jq -er '.inputs.base | .image + "@" + .digest' "$manifest")
        ;;
    steam|heroic)
        manifest=.build/context/apps/manifest.json
        test "$(jq -r .inputs.app "$manifest")" = "$profile"
        base=$(jq -er .inputs.base "$manifest")
        ;;
    *) exit 1 ;;
esac
[[ $base =~ @sha256:[a-f0-9]{64}$ ]] || { echo 'Package discovery needs an immutable base' >&2; exit 1; }
mkdir -p .build/context/packages
extra=()
if [ "$profile" = heroic ]; then extra=(-v "$PWD/.build/context/apps/heroic.deb:/artifact/heroic.deb:ro"); fi
temporary=".build/context/packages/$profile.plan.partial"
trap 'rm -f "$temporary"' EXIT
docker run --rm --platform linux/amd64 \
    -v "$PWD/docker/packages:/definitions:ro" \
    -v "$PWD/scripts/package-plan.sh:/planner.sh:ro" "${extra[@]}" \
    --entrypoint bash "$base" /planner.sh "$profile" > "$temporary"
mv "$temporary" ".build/context/packages/$profile.plan"
