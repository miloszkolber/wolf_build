# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS common
ENV DEBIAN_FRONTEND=noninteractive
COPY docker/apps/trim.sh /opt/app/trim.sh
COPY docker/apps/asound.conf /etc/asound.conf
COPY scripts/install-packages.sh /install-packages.sh
COPY .build/context/packages/common.lock /package-locks/common.lock
# Wolf supplies Wayland/Pulse sockets, per-user home and input devices.
# Applications need both ABIs for Proton/Wine, not a second audio server.
RUN dpkg --add-architecture i386 \
    && bash /install-packages.sh /package-locks/common.lock \
    && locale-gen en_US.UTF-8 \
    && userdel ubuntu && groupadd -g 1000 retro \
    && useradd -m -u 1000 -g retro -s /bin/bash retro \
    && bash /opt/app/trim.sh
ENV HOME=/home/retro UNAME=retro PUID=1000 PGID=1000 \
    XDG_RUNTIME_DIR=/run/user/1000 LANG=en_US.UTF-8 \
    WLR_BACKENDS=wayland WLR_LIBINPUT_NO_DEVICES=1 RUN_GAMESCOPE=1 PATH=/usr/games:$PATH
ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/opt/app/entrypoint.sh"]

FROM common AS steam
COPY .build/context/packages/steam.lock /licenses/application-packages.lock
RUN bash /install-packages.sh /licenses/application-packages.lock \
    && mkdir -p /etc/NetworkManager/conf.d \
    && touch /etc/NetworkManager/conf.d/10-globally-managed-devices.conf \
    && bash /opt/app/trim.sh && rm /install-packages.sh
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
COPY .build/context/packages/heroic.lock /licenses/application-packages.lock
# Bind the verified asset: copying it first would keep the 128 MB deb in an
# immutable layer even after the installer removes the file.
RUN --mount=type=bind,source=.build/context/apps,target=/artifact,ro \
    cd /artifact && sha256sum -c heroic.sha256 \
    && bash /install-packages.sh /licenses/application-packages.lock /artifact/heroic.deb \
    && bash /opt/app/trim.sh && rm -f /install-packages.sh
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
