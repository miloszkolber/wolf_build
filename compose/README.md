# Deployment example

The shared gate comes from `llama_build`. This repository builds only the Wolf runtime. One `.env` supplies both containers. The earlier gate-only template is replaced by this complete example, with no JSON config, gate build context or duplicate gate implementation.

## Configure and validate

Copy `.env.example` to `.env`. Select accepted image digests, state/socket directories and the actual socket/render groups. Read the `hidraw` major from `/proc/devices`. The DRM device paths are examples. Keep `GATE_CONTAINER_NAME` and `GATE_RUNTIME` aligned with the deployed names and activity prefixes aligned with upstream application-container names.

```sh
cp compose/.env.example compose/.env
docker compose --env-file compose/.env -f compose/docker-compose.yaml --profile runtime config --quiet
```

Validation does not create or start containers, prove device permissions or establish GPU support. There is no accepted Wolf `latest` until the first real session acceptance and protected promotion. Use a candidate digest explicitly for isolated testing, never pretend the placeholder tag exists.

## Authority and device boundary

Gate is read-only, non-root and device-free. Its Docker socket grants daemon authority, not isolation. The runtime has a writable filesystem for upstream startup and owns state, DRM, uinput, uhid and udev access. No privileged flag is used.

The `/dev` bind is intentional for upstream hotplug: `runners/docker.cpp` discovers newly created `/dev/input` and `/dev/hidraw*` nodes after startup, including virtual DualSense devices. Device cgroups allow dynamic input/hidraw access while DRM access is selected explicitly. The broad bind and Docker socket make this a trusted service, not a sandbox. Removing it requires a tested alternative for dynamic devices, not simply deleting a mount.

State and socket bind mounts let Wolf introspect their host paths when launching application containers. Pairing certificates, TOML and game state are runtime-owned. Steam/Lutris images remain upstream artifacts, outside this repository's build/update pipeline.

## Authorized rollout and recovery

Stop sessions and take a consistent backup of Wolf/app state before testing upgrades. Preserve both previous image digests and previous deployment settings. Check whether the selected upstream revision migrates state before relying on image rollback. Image rollback does not undo data migration.

Only during an authorized idle rollout, create the runtime without starting it and bring up gate:

```sh
docker compose --env-file compose/.env -f compose/docker-compose.yaml --profile runtime create wolf-runtime
docker compose --env-file compose/.env -f compose/docker-compose.yaml up -d wolf
```

Gate starts runtime on traffic and stops it after idle expiry with no matching application containers. The UDP trigger is dropped for client retry. Runtime readiness requires Docker health and configured TCP listeners. Gate `--health` checks only binary execution. Gate restart can stop the runtime, so do not roll it during a session.

A host updater may pull/recreate a changed runtime only while runtime and application sessions are stopped. Never attach Watchtower to the runtime or treat new candidate publication as automatic host deployment.
