# Deployment example

The shared gate comes from `llama_build`. Compose manages gate and runtime. Wolf launches this repository's Steam and Heroic images separately. Fixed names, protocol settings, gate digest, Docker socket and state mounts live in YAML. `.env` contains only the tested Wolf image and device/group settings. No JSON gate config or duplicate gate build is needed.

## Configure and validate

Copy `.env.example` to `.env`. Set an exact tested Wolf image digest and the actual socket/render groups. Read the `hidraw` major from `/proc/devices`. The DRM device paths are examples. Edit Compose directly for one-off changes to names, paths, gate image or timeouts. If names change, update gate's matching environment values too. Runtime image defaults supply logging, Intel driver selection and shutdown behavior without repeating them in `.env`.

Prefer the selected discrete GPU's `/dev/dri/by-path/` render symlink for `WOLF_RENDER_NODE`. The example maps the DRM directory so each container start enumerates current node numbers. This does not enable another GPU, but it exposes all DRM devices already enabled on the host. If multiple GPUs are enabled, restrict access according to the deployment's device policy.

```sh
cp compose/.env.example compose/.env
docker compose --env-file compose/.env -f compose/docker-compose.yaml --profile runtime config --quiet
```

Validation does not create/start containers or prove device/GPU access. Operator-approved testing `latest` may precede complete game/session acceptance. Select a real tested digest, not the placeholder value.

## Authority and device boundary

Gate is read-only, non-root and device-free. Its Docker socket grants daemon authority, not isolation. The runtime has a writable filesystem for upstream startup and owns state, DRM, uinput, uhid and udev access. No privileged flag is used.

The `/dev` bind is intentional for upstream hotplug: `runners/docker.cpp` discovers newly created `/dev/input` and `/dev/hidraw*` nodes after startup, including virtual DualSense devices. Device cgroups allow dynamic input/hidraw access while DRM access is selected explicitly. The broad bind and Docker socket make this a trusted service, not a sandbox. Removing it requires a tested alternative for dynamic devices, not simply deleting a mount.

State and socket bind mounts let Wolf introspect their host paths when launching application containers. Pairing certificates, TOML and game state are runtime-owned. [Steam and Heroic candidates](apps.md) are built and maintained here. Existing configurations are not silently migrated to them.

Keep the saved application runner rules consistent as fallback, as described in [application integration](apps.md). The pinned Wolf runner normally discovers and injects the current majors at creation. Runtime grants do not transfer to sibling containers.

## Authorized rollout and recovery

Stop sessions and take a consistent backup of Wolf/app state before testing upgrades. Preserve both previous image digests and previous deployment settings. Check whether the selected upstream revision migrates state before relying on image rollback. Image rollback does not undo data migration.

Only during an authorized idle rollout, create the runtime without starting it and bring up gate:

```sh
docker compose --env-file compose/.env -f compose/docker-compose.yaml --profile runtime create wolf-runtime
docker compose --env-file compose/.env -f compose/docker-compose.yaml up -d wolf
```

Gate starts runtime on traffic and stops it after idle expiry with no matching application containers. Wolf stops a stream session after 900 seconds without a client (`WOLF_SESSION_IDLE_TIMEOUT` on the runtime, `0` disables it), so a TV that is switched off ends the application container and the gate's idle stop follows. The UDP trigger is dropped for client retry. Runtime readiness requires Docker health and configured TCP listeners. Gate `--health` checks only binary execution. Gate restart can stop the runtime, so do not roll it during a session.

The gate's plaintext discovery cache covers Wolf's `/serverinfo` on the control port. After a gate-started runtime answers it, the same GET or HEAD from that client host is answered while the runtime is stopped, so a client that keeps polling discovery does not cycle the runtime. The cache lives in the gate process, so the first probe after a gate restart starts the runtime once, and a different host name or path also starts it. Encrypted discovery still starts the runtime.

A host updater may pull/recreate a changed runtime only while runtime and application sessions are stopped. Never attach Watchtower to the runtime or treat new candidate publication as automatic host deployment.

Embedded PulseAudio failure shuts down the whole runtime through supervisor so Wolf follows its normal session teardown. Restarting Pulse alone would lose virtual sinks and leave stale Wolf connections. Pulse diagnostics are forwarded to container logs, and runtime health also requires a successful bounded Pulse query. The gate may start a fresh runtime on the next request. This policy ends games on an audio-server failure rather than claiming seamless recovery.

A live GPU reset is not transparent recovery. Existing GPU handles can fail, and directory mappings do not automatically grant newly allocated DRM minors to an already-running container. Stop affected GPU consumers during an authorized idle recovery, recover the driver and then start or recreate consumers with the current devices. Do not reset an active GPU merely because a health endpoint succeeds while video fails.
