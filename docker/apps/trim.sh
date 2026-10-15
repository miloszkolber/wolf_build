#!/bin/bash
set -euo pipefail
# These are separate Vulkan drivers, not Mesa's shared Gallium/LLVM closure.
# Delete in the package-install layer so omitted files never occupy image layers.
mkdir -p /licenses
# The Ubuntu base bundles an unowned service manager. These images use tini.
if [ -e /usr/bin/pebble ]; then
    echo /usr/bin/pebble >> /licenses/pruned-files.txt
    rm /usr/bin/pebble
fi
for directory in /usr/lib/x86_64-linux-gnu /usr/lib/i386-linux-gnu; do
    find "$directory" -maxdepth 1 -type f -name 'libvulkan_*.so' \
        ! -name 'libvulkan_intel*.so' -print -delete >> /licenses/pruned-files.txt
done
find /usr/share/vulkan/icd.d -type f ! -name 'intel*.json' -print -delete >> /licenses/pruned-files.txt
