# syntax=docker/dockerfile:1
ARG BASE_IMAGE
ARG RUST_IMAGE
FROM ${RUST_IMAGE} AS rust
FROM ${BASE_IMAGE} AS build
ENV DEBIAN_FRONTEND=noninteractive
ARG SECURITY_REFRESH
RUN test -n "$SECURITY_REFRESH" \
    && apt-get -o APT::Update::Error-Mode=any -o Acquire::Retries=5 update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
    build-essential clang cmake ninja-build pkg-config python3 meson bison flex nasm \
    git ca-certificates autoconf automake libtool gettext curl \
    libboost-all-dev libssl-dev libcurl4-openssl-dev libunwind-dev libevdev-dev \
    libinput-dev libxkbcommon-dev libwayland-dev wayland-protocols libgbm-dev \
    libegl-dev libgles-dev libopengl-dev libdrm-dev libpci-dev libpulse-dev \
    libudev-dev libglib2.0-dev libopus-dev libaom-dev libx264-dev libx265-dev \
    libcap-dev libdw-dev libgudev-1.0-dev libx11-xcb-dev libxfixes-dev \
    libxdamage-dev libxrandr-dev libxcb-dri3-dev libxcb-present-dev \
    liborc-0.4-dev libjpeg-dev libpng-dev libdwarf-dev libicu-dev libzstd-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup
ENV PATH=/usr/local/cargo/bin:/opt/wolf-runtime/bin:$PATH \
    RUSTUP_HOME=/usr/local/rustup CARGO_HOME=/usr/local/cargo \
    PKG_CONFIG_PATH=/opt/wolf-runtime/lib/pkgconfig \
    LD_LIBRARY_PATH=/opt/wolf-runtime/lib \
    C_INCLUDE_PATH=/opt/wolf-runtime/include CPLUS_INCLUDE_PATH=/opt/wolf-runtime/include
COPY .build/context/sources/ /sources/
COPY scripts/compile-runtime.sh /compile-runtime.sh
ARG BUILD_JOBS=2
ENV BUILD_JOBS=${BUILD_JOBS}
RUN bash /compile-runtime.sh gmmlib
RUN bash /compile-runtime.sh libva
RUN bash /compile-runtime.sh media-driver
RUN bash /compile-runtime.sh libvpl
RUN bash /compile-runtime.sh vpl-gpu-rt
COPY scripts/compile-gstreamer.sh /compile-gstreamer.sh
RUN bash /compile-gstreamer.sh gstreamer
RUN bash /compile-gstreamer.sh interpipe
COPY scripts/compile-compositor.sh /compile-compositor.sh
COPY scripts/collect-rust-licenses.py /collect-rust-licenses.py
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    bash /compile-compositor.sh
COPY .build/context/locked-sources.cmake /locked-sources.cmake
COPY scripts/compile-wolf.sh /compile-wolf.sh
RUN bash /compile-wolf.sh

FROM ${BASE_IMAGE} AS runtime
ENV DEBIAN_FRONTEND=noninteractive
ARG SECURITY_REFRESH
RUN test -n "$SECURITY_REFRESH" \
    && rm -f /usr/bin/pebble \
    && apt-get -o APT::Update::Error-Mode=any -o Acquire::Retries=5 update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
    ca-certificates bash python3 supervisor pulseaudio pulseaudio-utils \
    libssl3t64 libicu78 libcurl4t64 libunwind8 libevdev2 libinput10 \
    libxkbcommon0 libwayland-server0 libwayland-client0 libwayland-cursor0 libwayland-egl1 libgbm1 libegl1 \
    libgles2 libgl1 libopengl0 libdrm2 libpci3 libudev1 libglib2.0-0t64 \
    libopus0 libaom3 libx264-165 libx265-215 libcap2 libdw1t64 libgudev-1.0-0 \
    libx11-xcb1 libxfixes3 libxdamage1 libxrandr2 liborc-0.4-0t64 \
    libjpeg-turbo8 libpng16-16t64 xwayland hwdata libdwarf1 libquadmath0 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /opt/wolf-runtime/ /opt/wolf-runtime/
COPY --from=build /wolf/ /wolf/
COPY --from=build /sources/wolf/docker/startup.sh /startup.sh
COPY --from=build /sources/wolf/docker/supervisord.conf /etc/supervisord.conf
COPY .build/context/licenses/ /licenses/sources/
COPY .build/context/manifest.json /licenses/manifest.json
COPY scripts/check-runtime.py /app/check-runtime.py
ENV PATH=/opt/wolf-runtime/bin:$PATH \
    LD_LIBRARY_PATH=/opt/wolf-runtime/lib \
    LIBVA_DRIVERS_PATH=/opt/wolf-runtime/lib/dri LIBVA_DRIVER_NAME=iHD \
    GST_PLUGIN_PATH=/opt/wolf-runtime/lib/gstreamer-1.0 \
    GST_PLUGIN_SYSTEM_PATH_1_0=/opt/wolf-runtime/lib/gstreamer-1.0 \
    GST_GL_API=gles2 GST_GL_PLATFORM=egl GST_GL_WINDOW=surfaceless \
    HOST_APPS_STATE_FOLDER=/etc/wolf WOLF_CFG_FOLDER=/etc/wolf/cfg \
    WOLF_CFG_FILE=/etc/wolf/cfg/config.toml \
    WOLF_PRIVATE_KEY_FILE=/etc/wolf/cfg/key.pem WOLF_PRIVATE_CERT_FILE=/etc/wolf/cfg/cert.pem \
    WOLF_USE_ZERO_COPY=TRUE WOLF_LOG_LEVEL=INFO GST_DEBUG=2 \
    WOLF_RENDER_NODE=/dev/dri/renderD128 WOLF_STOP_CONTAINER_ON_EXIT=TRUE \
    WOLF_DOCKER_SOCKET=/var/run/docker.sock WOLF_DEFAULT_RUN_UID=1000 WOLF_DEFAULT_RUN_GID=1000 \
    WOLF_WAYLAND_SOCKET_WAIT_TIMEOUT_MS=5000 XDG_RUNTIME_DIR=/run/user/wolf TZ=UTC
RUN chmod 755 /startup.sh && python3 /app/check-runtime.py --static \
    && dpkg-query -W > /licenses/distribution-packages.txt
EXPOSE 47984/tcp 47989/tcp 48010/tcp 47999/udp 48100/udp 48200/udp
WORKDIR /wolf
ARG WOLF_SHA
ARG INPUT_SHA256
ARG RECIPE_REVISION
LABEL org.opencontainers.image.source="https://github.com/miloszkolber/wolf_build" \
      org.opencontainers.image.revision="${RECIPE_REVISION}" \
      io.wolf-build.wolf-revision="${WOLF_SHA}" \
      io.wolf-build.input-sha256="${INPUT_SHA256}"
ENTRYPOINT ["/bin/bash", "/startup.sh"]
HEALTHCHECK --interval=5s --timeout=3s --start-period=15s CMD ["python3", "/app/check-runtime.py", "--health"]
