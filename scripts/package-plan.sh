#!/bin/bash
# Runs inside the exact base image. No package installation or host authority.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive LC_ALL=C
profile=${1:?runtime, steam or heroic}
case "$profile" in
    runtime) stages=(build runtime) ;;
    steam|heroic) dpkg --add-architecture i386; stages=(common "$profile") ;;
    *) exit 1 ;;
esac
apt-get -o Acquire::Retries=5 -o APT::Update::Error-Mode=any update >&2
printf '@@installed\n'
dpkg-query -W -f='${Package}\t${Architecture}\t${Version}\n'
mapfile -t base < <(dpkg-query -W -f='${binary:Package}\n')
common=()
for stage in "${stages[@]}"; do
    files=("/definitions/$stage.txt")
    if [ "$profile" != runtime ] && [ "$stage" = "$profile" ]; then files=(/definitions/common.txt "${files[@]}"); fi
    mapfile -t roots < <(cat "${files[@]}" | tr -s '[:space:]' '\n' | grep -v '^$')
    extra=()
    if [ "$stage" = heroic ]; then extra=(/artifact/heroic.deb); fi
    printf '@@%s\n' "$stage"
    # Explicit base roots include inherited security updates, not only new deps.
    plan=$(apt-get --simulate --no-install-recommends install "${base[@]}" "${common[@]}" "${roots[@]}" "${extra[@]}")
    printf '%s\n' "$plan"
    if [ "$stage" = common ]; then
        # The target inherits every installed common dependency, including an
        # alternative provider the target alone would not select (e.g. seatd).
        mapfile -t common < <(awk '$1 == "Inst" {print $2}' <<< "$plan")
    fi
done
