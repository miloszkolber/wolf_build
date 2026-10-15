#!/bin/bash
set -euo pipefail
kind=${1:?steam or lutris}
for executable in sway Xwayland gosu tini dbus-run-session bwrap; do command -v "$executable"; done
case "$kind" in
steam) command -v steam; dpkg-query -W steam-installer steam-libs:i386 ;;
lutris) command -v lutris; dpkg-query -W lutris wine64 wine32:i386; gosu retro lutris --version ;;
*) exit 1 ;;
esac
for arch in x86_64-linux-gnu i386-linux-gnu; do
    test -e "/usr/lib/$arch/libvulkan_intel.so"
    test -e "/usr/lib/$arch/dri/iris_dri.so"
    test -e "/usr/lib/$arch/libpulse.so.0"
    for library in "/usr/lib/$arch/libvulkan_intel.so" "/usr/lib/$arch/dri/iris_dri.so"; do
        closure=$(ldd "$library")
        if grep -q 'not found' <<< "$closure"; then printf '%s\n' "$closure" >&2; exit 1; fi
    done
done
test -z "$(find /usr/share/vulkan/icd.d -type f ! -name 'intel*.json' -print -quit)"
for package in pulseaudio supervisor network-manager bluez clang gcc; do
    if dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null | grep -qx installed; then
        echo "Unwanted application-image package: $package" >&2; exit 1
    fi
done
for script in /opt/app/*.sh; do bash -n "$script"; done
mkdir -p /licenses
dpkg-query -W -f='${binary:Package}\t${Version}\n' > /licenses/distribution-packages.txt
test -s /licenses/manifest.json
echo 'Application payload checked; session/GPU/game acceptance not established.'
