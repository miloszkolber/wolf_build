ARG IMAGE
FROM ${IMAGE} AS compiler
USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc gcc-multilib libc6-dev-i386
COPY play.c /play.c
RUN gcc -m64 /play.c -ldl -o /play64 && gcc -m32 /play.c -ldl -o /play32

FROM ${IMAGE} AS audio-server
USER root
RUN apt-get update && apt-get install -y --no-install-recommends pulseaudio pulseaudio-utils python3 && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/bin/bash", "-ec"]
CMD ["mkdir -m 700 /tmp/runtime; exec pulseaudio -n --daemonize=false --exit-idle-time=-1 --load='module-native-protocol-unix auth-anonymous=1 socket=/audio/pulse' --load='module-null-sink sink_name=decoy rate=48000 channels=2' --load='module-null-sink sink_name=session-test rate=48000 channels=2'"]

FROM ${IMAGE} AS audio-client
# Only the test executables cross from compiler. The client's runtime libraries
# and configuration remain exactly those of the final application image.
COPY --from=compiler /play64 /play32 /audio-test/
ENTRYPOINT ["/audio-test/play64"]
