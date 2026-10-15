#!/bin/bash
set -euo pipefail
prefix=/opt/wolf-runtime
jobs=${BUILD_JOBS:-2}
cd /sources/compositor
# Wolf consumes the GStreamer factory, not the standalone C API libraries.
cargo build --locked --release -p gst-plugin-wayland-display -j "$jobs"
install -Dm755 target/release/libgstwaylanddisplaysrc.so "$prefix/lib/gstreamer-1.0/libgstwaylanddisplaysrc.so"
python3 /collect-rust-licenses.py
