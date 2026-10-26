#!/bin/bash
set -euo pipefail
prefix=/opt/wolf-runtime
jobs=${BUILD_JOBS:-2}
if [ "$1" = gstreamer ]; then
    # 1.28 plugin docs request gstcheck's doc-cache generator before honouring
    # -Ddoc=disabled, and auto_features=disabled turns check off. Keep the
    # core subproject's check library enabled so configure works; tests and
    # documentation stay disabled.
    meson setup /build/gstreamer /sources/gstreamer --prefix="$prefix" --libdir=lib \
        --buildtype=release --strip --wrap-mode=nofallback -Dauto_features=disabled \
        -Dbase=enabled -Dgood=enabled -Dbad=enabled -Dugly=enabled -Dgpl=enabled \
        -Dtools=enabled -Dorc=enabled \
        -Dgst-plugins-base:app=enabled -Dgst-plugins-base:audioconvert=enabled \
        -Dgst-plugins-base:audioresample=enabled -Dgst-plugins-base:audiorate=enabled \
        -Dgst-plugins-base:opus=enabled \
        -Dgst-plugins-base:videoconvertscale=enabled -Dgst-plugins-base:videotestsrc=enabled \
        -Dgst-plugins-base:audiotestsrc=enabled \
        -Dgst-plugins-base:gl=enabled -Dgst-plugins-base:gl_winsys=wayland,egl,gbm,surfaceless \
        -Dgst-plugins-good:pulse=enabled -Dgst-plugins-good:udp=enabled \
        -Dgst-plugins-good:rtp=enabled -Dgst-plugins-good:rtpmanager=enabled \
        -Dgst-plugins-bad:videoparsers=enabled -Dgst-plugins-bad:va=enabled \
        -Dgst-plugins-bad:qsv=enabled -Dgst-plugins-bad:x265=enabled \
        -Dgst-plugins-bad:aom=enabled -Dgst-plugins-ugly:x264=enabled \
        -Dtests=disabled -Dexamples=disabled -Ddoc=disabled -Dgstreamer:check=enabled
    meson compile -C /build/gstreamer -j "$jobs"
    meson install -C /build/gstreamer
elif [ "$1" = interpipe ]; then
    # Upstream declares its test-only gst-check dependency even with tests off.
    python3 - <<'PY'
from pathlib import Path
path=Path('/sources/interpipe/meson.build')
text=path.read_text()
old="gst_check_dep = dependency('gstreamer-check-1.0', version : '>=1.0.5')"
new="gst_check_dep = dependency('gstreamer-check-1.0', version : '>=1.0.5', required : get_option('tests'))"
if text.count(old)!=1: raise SystemExit('Interpipe dependency declaration changed; review build compatibility')
path.write_text(text.replace(old,new))
PY
    meson setup /build/interpipe /sources/interpipe --prefix="$prefix" --libdir=lib \
        --buildtype=release --strip --wrap-mode=nofallback -Denable-gtk-doc=false -Dtests=disabled
    meson compile -C /build/interpipe -j "$jobs"
    meson install -C /build/interpipe
else
    echo "Unknown GStreamer phase: $1" >&2; exit 2
fi
