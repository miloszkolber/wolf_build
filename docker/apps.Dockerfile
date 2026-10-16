# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS common
ARG REFRESH
ENV DEBIAN_FRONTEND=noninteractive
COPY docker/apps/trim.sh /opt/app/trim.sh
# Wolf supplies Wayland/Pulse sockets, per-user home and input devices.
# Applications need both ABIs for Proton/Wine, not a second audio server.
RUN test -n "$REFRESH" && dpkg --add-architecture i386 \
    && apt-get -o Acquire::Retries=5 -o APT::Update::Error-Mode=any update \
    && apt-get -o Acquire::Retries=5 upgrade -y --no-install-recommends \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
       ca-certificates bash tini gosu passwd dbus-daemon \
       sway xwayland x11-utils xauth xdg-utils fonts-dejavu-core locales \
       bubblewrap libudev1 libinput10 libevdev2 libnss3 \
       libgl1-mesa-dri:amd64 libgl1-mesa-dri:i386 \
       mesa-vulkan-drivers:amd64 mesa-vulkan-drivers:i386 \
       libvulkan1:amd64 libvulkan1:i386 libegl1:amd64 libegl1:i386 \
       libasound2-plugins:amd64 libasound2-plugins:i386 libpulse0:amd64 libpulse0:i386 \
    && locale-gen en_US.UTF-8 && rm -rf /var/lib/apt/lists/* \
    && userdel ubuntu && groupadd -g 1000 retro \
    && useradd -m -u 1000 -g retro -s /bin/bash retro \
    && bash /opt/app/trim.sh
ENV HOME=/home/retro UNAME=retro PUID=1000 PGID=1000 \
    XDG_RUNTIME_DIR=/run/user/1000 LANG=en_US.UTF-8 \
    WLR_BACKENDS=wayland WLR_LIBINPUT_NO_DEVICES=1 PATH=/usr/games:$PATH
ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/opt/app/entrypoint.sh"]

FROM common AS steam
RUN apt-get -o Acquire::Retries=5 -o APT::Update::Error-Mode=any update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
       steam-installer network-manager dbus-system-bus-common util-linux \
    && mkdir -p /etc/NetworkManager/conf.d \
    && touch /etc/NetworkManager/conf.d/10-globally-managed-devices.conf \
    && bash /opt/app/trim.sh && rm -rf /var/lib/apt/lists/*
ENV APP_KIND=steam
COPY docker/apps/ /opt/app/
COPY .build/context/apps/manifest.json /licenses/manifest.json
RUN chmod 755 /opt/app/*.sh && /opt/app/check.sh steam
LABEL org.opencontainers.image.title="wolf_steam" \
      org.opencontainers.image.description="Minimal Steam application image for the Intel-only Wolf runtime" \
      org.opencontainers.image.source="https://github.com/miloszkolber/wolf_build"
ARG INPUT_SHA256
LABEL io.wolf-build.input-sha256="${INPUT_SHA256}"
CMD ["/opt/app/launch.sh"]

FROM common AS heroic
COPY .build/context/apps/heroic.deb /tmp/heroic.deb
COPY .build/context/apps/heroic.sha256 /tmp/heroic.sha256
RUN cd /tmp && sha256sum -c heroic.sha256 \
    && apt-get -o Acquire::Retries=5 -o APT::Update::Error-Mode=any update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
       /tmp/heroic.deb curl unzip pciutils xdg-user-dirs python3 \
    && rm -f /tmp/heroic.deb /tmp/heroic.sha256 && rm -rf /var/lib/apt/lists/* \
    && bash /opt/app/trim.sh
ENV APP_KIND=heroic
COPY docker/apps/ /opt/app/
COPY .build/context/apps/manifest.json /licenses/manifest.json
RUN chmod 755 /opt/app/*.sh && /opt/app/check.sh heroic
LABEL org.opencontainers.image.title="wolf_heroic" \
      org.opencontainers.image.description="GOG-first Heroic Console Mode application image for the Intel-only Wolf runtime" \
      org.opencontainers.image.source="https://github.com/miloszkolber/wolf_build"
ARG INPUT_SHA256
LABEL io.wolf-build.input-sha256="${INPUT_SHA256}"
CMD ["/opt/app/launch.sh"]
