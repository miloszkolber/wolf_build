#!/bin/bash
set -euo pipefail
prefix=/opt/wolf-runtime
jobs=${BUILD_JOBS:-2}
cmake -S /sources/wolf -B /build/wolf -G Ninja -C /locked-sources.cmake \
    -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_CXX_FLAGS="--gcc-install-dir=$(dirname "$(gcc -print-libgcc-file-name)")" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$prefix" \
    -DBUILD_SHARED_LIBS=OFF -DBoost_USE_STATIC_LIBS=ON \
    -DBUILD_FAKE_UDEV_CLI=ON -DBUILD_TESTING=OFF -DADD_STACKTRACE_INFO=OFF \
    -DCPPTRACE_USE_EXTERNAL_LIBDWARF=ON -DCPPTRACE_USE_EXTERNAL_ZSTD=ON \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON
cmake --build /build/wolf --target wolf fake-udev --parallel "$jobs"
mkdir /wolf
cp /build/wolf/src/moonlight-server/wolf /build/wolf/src/fake-udev/fake-udev /wolf/
strip /wolf/*
mkdir -p "$prefix/share/licenses/boost"
for license in /usr/share/doc/libboost[0-9]*-dev/copyright; do
    if [ -f "$license" ]; then cp "$license" "$prefix/share/licenses/boost/copyright"; break; fi
done
test -s "$prefix/share/licenses/boost/copyright"
dpkg-query -W > "$prefix/share/licenses/build-packages.txt"
rm -rf "$prefix/include" "$prefix/lib/pkgconfig" "$prefix/lib/cmake"
find "$prefix" -type f \( -name '*.a' -o -name '*.la' \) -delete
