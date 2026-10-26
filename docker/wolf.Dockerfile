# syntax=docker/dockerfile:1
ARG BASE_IMAGE
ARG RUST_IMAGE
FROM ${RUST_IMAGE} AS rust
FROM ${BASE_IMAGE} AS build
ENV DEBIAN_FRONTEND=noninteractive
COPY scripts/install-packages.sh /install-packages.sh
COPY .build/context/packages/build.lock /package-locks/build.lock
RUN bash /install-packages.sh /package-locks/build.lock
COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup
ENV PATH=/usr/local/cargo/bin:/opt/wolf-runtime/bin:$PATH \
    RUSTUP_HOME=/usr/local/rustup CARGO_HOME=/usr/local/cargo \
    PKG_CONFIG_PATH=/opt/wolf-runtime/lib/pkgconfig \
    LD_LIBRARY_PATH=/opt/wolf-runtime/lib \
    C_INCLUDE_PATH=/opt/wolf-runtime/include CPLUS_INCLUDE_PATH=/opt/wolf-runtime/include
COPY scripts/compile-runtime.sh /compile-runtime.sh
ARG BUILD_JOBS=2
ENV BUILD_JOBS=${BUILD_JOBS}
COPY .build/context/sources/gmmlib/ /sources/gmmlib/
RUN bash /compile-runtime.sh gmmlib
COPY .build/context/sources/libva/ /sources/libva/
RUN bash /compile-runtime.sh libva
COPY .build/context/sources/media-driver/ /sources/media-driver/
RUN bash /compile-runtime.sh media-driver
COPY .build/context/sources/libvpl/ /sources/libvpl/
RUN bash /compile-runtime.sh libvpl
COPY .build/context/sources/vpl-gpu-rt/ /sources/vpl-gpu-rt/
RUN bash /compile-runtime.sh vpl-gpu-rt
COPY scripts/compile-gstreamer.sh /compile-gstreamer.sh
COPY .build/context/sources/gstreamer/ /sources/gstreamer/
RUN bash /compile-gstreamer.sh gstreamer
COPY .build/context/sources/interpipe/ /sources/interpipe/
RUN bash /compile-gstreamer.sh interpipe
COPY .build/context/sources/compositor/ /sources/compositor/
COPY scripts/compile-compositor.sh /compile-compositor.sh
COPY scripts/collect-rust-licenses.py /collect-rust-licenses.py
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    bash /compile-compositor.sh
COPY .build/context/locked-sources.cmake /locked-sources.cmake
COPY .build/context/sources/wolf/ /sources/wolf/
# All FetchContent dependencies have wolf-* names. build-inputs.py prepares
# this subset without moving a Wolf-only change ahead of the Intel builds.
COPY .build/context/wolf-dependencies/ /sources/
COPY scripts/compile-wolf.sh /compile-wolf.sh
RUN bash /compile-wolf.sh

FROM ${BASE_IMAGE} AS runtime
ENV DEBIAN_FRONTEND=noninteractive
COPY scripts/install-packages.sh /install-packages.sh
COPY .build/context/packages/runtime.lock /licenses/runtime-packages.lock
RUN rm -f /usr/bin/pebble && bash /install-packages.sh /licenses/runtime-packages.lock \
    && rm /install-packages.sh
COPY --from=build /opt/wolf-runtime/ /opt/wolf-runtime/
COPY --from=build /wolf/ /wolf/
COPY --from=build /sources/wolf/docker/startup.sh /startup.sh
COPY --from=build /sources/wolf/docker/supervisord.conf /etc/supervisord.conf
COPY docker/runtime/wolf-session-idle.conf /etc/supervisor/conf.d/wolf-session-idle.conf
COPY docker/runtime/wolf-audio-failure.conf /etc/supervisor/conf.d/wolf-audio-failure.conf
COPY docker/runtime/configure-supervisor.py /app/configure-supervisor.py
RUN python3 /app/configure-supervisor.py /etc/supervisord.conf
# Session helpers live beside Wolf in the same supervisor. Preserve upstream's
# Wolf shutdown settings and include the observer and audio-failure listener.
RUN printf '\n[include]\nfiles = /etc/supervisor/conf.d/*.conf\n' >> /etc/supervisord.conf
COPY .build/context/licenses/ /licenses/sources/
COPY .build/context/manifest.json /licenses/manifest.json
COPY scripts/check-runtime.py /app/check-runtime.py
COPY scripts/wolf-session-idle.py /app/wolf-session-idle.py
COPY scripts/wolf-audio-failure.py /app/wolf-audio-failure.py
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
LABEL org.opencontainers.image.title="wolf_runtime" \
      org.opencontainers.image.description="Intel-only Wolf streaming runtime with embedded audio and hardware encoding" \
      org.opencontainers.image.source="https://github.com/miloszkolber/wolf_build" \
      org.opencontainers.image.revision="${RECIPE_REVISION}" \
      io.wolf-build.wolf-revision="${WOLF_SHA}" \
      io.wolf-build.input-sha256="${INPUT_SHA256}"
ENTRYPOINT ["/bin/bash", "/startup.sh"]
HEALTHCHECK --interval=5s --timeout=3s --start-period=15s CMD ["python3", "/app/check-runtime.py", "--health"]
