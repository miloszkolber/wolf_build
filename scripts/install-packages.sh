#!/bin/bash
# Consume the exact solver closure and reject repository drift rather than float.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive LC_ALL=C
lock=${1:?package lock}
shift
mapfile -t packages < "$lock"
test "${#packages[@]}" -gt 0
apt-get -o Acquire::Retries=5 -o APT::Update::Error-Mode=any update
apt-get -o Acquire::Retries=5 install -y --no-install-recommends "${packages[@]}" "$@"
actual=$(dpkg-query -W -f='${Package}\t${Architecture}\t${Version}\n' | \
    awk -F '\t' '{print $1 ($2 == "all" ? "" : ":" $2) "=" $3}' | sort)
expected=$(sort "$lock")
if [ "$actual" != "$expected" ]; then
    printf 'Installed package closure differs from the resolved lock\n%s\n' "$actual" >&2
    exit 1
fi
rm -rf /var/lib/apt/lists/*
