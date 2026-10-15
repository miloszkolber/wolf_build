#!/bin/bash
set -euo pipefail
prefix=/opt/wolf-runtime
jobs=${BUILD_JOBS:-2}
mkdir -p "$prefix"
export CMAKE_PREFIX_PATH="$prefix"
cmake_install() {
    local name=$1; shift
    cmake -S "/sources/$name" -B "/build/$name" -G Ninja \
        -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
        -DCMAKE_CXX_FLAGS="--gcc-install-dir=$(dirname "$(gcc -print-libgcc-file-name)")" \
        -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$prefix" \
        -DCMAKE_INSTALL_LIBDIR=lib "$@"
    cmake --build "/build/$name" --parallel "$jobs"
    cmake --install "/build/$name"
}
case "$1" in
gmmlib) cmake_install gmmlib -DRUN_TEST_SUITE=OFF ;;
libva)
meson setup /build/libva /sources/libva --prefix="$prefix" --libdir=lib \
    --buildtype=release -Dwith_x11=yes -Dwith_wayland=yes
meson compile -C /build/libva -j "$jobs"
meson install -C /build/libva
;;
media-driver) cmake_install media-driver -DBUILD_TESTING=OFF ;;
libvpl) cmake_install libvpl -DBUILD_TOOLS=OFF -DBUILD_TESTS=OFF ;;
vpl-gpu-rt) cmake_install vpl-gpu-rt -DBUILD_TESTING=OFF ;;

*) echo "Unknown build phase: $1" >&2; exit 2 ;;
esac
