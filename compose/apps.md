# Steam and Lutris images

This repository builds `ghcr.io/<owner>/wolf_steam` and `ghcr.io/<owner>/wolf_lutris` from its own [Dockerfile](../docker/apps.Dockerfile). Operator-approved `latest` releases may be tested before full streaming/game acceptance. Use exact digests for controlled rollout and rollback.

## Payload and compatibility

Both targets use a digest-pinned Ubuntu 26.04 base, package-managed Sway/Xwayland, a small session D-Bus, non-root application processes and Mesa/ALSA/Pulse client libraries for amd64 and i386. The 32-bit libraries are required by Steam/Proton/Wine. PulseAudio's server remains in Wolf. There is no second audio container, desktop environment, panel, terminal, NVIDIA integration, Decky loader, gamescope build or copied upstream base-app image.

Steam installs Ubuntu's `steam-installer` with no recommended packages. Valve's client, Proton and games update in the persistent user home, not in a fabricated immutable Steam-client version. Their runtime updates are outside the distribution package inventory.

Lutris resolves its latest stable upstream `.deb` before building and checks the GitHub-published SHA256 twice, during acquisition and assembly. Wine, winetricks and multimedia dependencies come from signed distribution repositories. The frontend is standard GTK Lutris, not a separate AppImage/gamepad UI. Controller input in games remains required acceptance, but controller-only library navigation is not claimed. No custom bubblewrap patch removes capability checks. App containers must not add `SYS_ADMIN` solely to bypass an upstream image assumption. User-namespace availability and the target host's security policy require explicit acceptance.

The build removes separate non-Intel Vulkan drivers and ICD registrations in the package-install layer and records every removed file. It keeps Mesa's shared Gallium/LLVM libraries because distro packaging shares them with Intel rendering. OpenGL software rendering remains available, but software/non-Intel Vulkan is intentionally excluded. The image smoke check verifies Intel Vulkan/DRI library closure and Pulse clients for both ABIs and rejects unwanted audio servers, system network daemons and build tooling. Further pruning requires closure and game tests, not package-name heuristics.

## Build and dependency updates

Run Python in the development container, then Docker in the development Docker context:

```sh
python3 scripts/resolve-apps.py > .build/apps.json
docker build -f docker/apps.Dockerfile --target steam --build-arg BASE_IMAGE="$(jq -r .inputs.base .build/apps.json)" --build-arg REFRESH="$(jq -r .inputs.refresh .build/apps.json)" --build-arg INPUT_SHA256="$(jq -r .input_sha256 .build/apps.json)" -t wolf-steam:local .
```

Use target `lutris` for the second image. No GPU, Docker socket or production state is needed to build either target. The common stage is shared locally. [Application CI](../.github/workflows/apps.yml) runs daily, on application-source changes, PRs and manual dispatch. Daily cache invalidation upgrades packages inherited from the base as well as installing current application dependencies, even without a new Lutris release. There is no snapshot-mirror or distro-port maintenance layer.

Each image embeds the resolved base/release/recipe/refresh manifest, the exact installed package versions and package copyright files. CI records image size, CycloneDX SBOM and HIGH/CRITICAL vulnerability findings. It tests non-default UID/GID setup without devices/network. Failed checks prevent candidate publication. PRs cannot publish. Input-hash candidate tags are never overwritten. Installed packages are recorded, not claimed frozen for a later rebuild. Preserve the original tested digest for rollback.

## Wolf integration

Wolf creates these application containers, not Compose. It supplies `PUID`, `PGID`, `XDG_RUNTIME_DIR`, `WAYLAND_DISPLAY`, Pulse server/sink/source, linked DRM/input devices, fake-udev and the per-user `/home/retro` mount. The entrypoint keeps those paths and groups, changes ownership only on top-level writable directories and drops privileges before launching the application. It does not recursively rewrite game-library ownership.

During an authorized idle configuration change, keep existing application entries and state, then replace only their runner image references with the exact tested candidate digests:

```toml
# In the existing Steam runner:
image = "ghcr.io/<owner>/wolf_steam@sha256:<tested-digest>"
# In the existing Lutris runner:
image = "ghcr.io/<owner>/wolf_lutris@sha256:<tested-digest>"
```

Keep `start_virtual_compositor = true`, existing runner names and the shared Lutris mount at `/var/lutris`. Remove NVIDIA-only device requests for the Intel target. Review inherited capabilities: the custom application images do not need the upstream patched-bubblewrap `SYS_ADMIN` grant. Do not silently weaken host user-namespace or sandbox policy to make a game launch. The Lutris shared `Games`, `library` and `share` layout and existing per-user configs are preserved. Steam accepts simple `STEAM_STARTUP_FLAGS` including a game URL without evaluating it as shell code. These images always use nested Sway, so upstream `RUN_SWAY` values need no additional flag here. Gamescope-only settings and Decky/SteamOS integration are not implemented.

Before rollout, test both images with the exact Wolf candidate: first login/download, Steam/Proton game, Lutris native/Wine game, 32/64-bit Intel rendering, sound, keyboard/mouse/controller including hotplug, library persistence, normal exit, reconnect and idle cleanup. Retain prior digests/configuration and back up state. Source checks and software rendering do not establish this acceptance.

The shared [promotion workflow](../.github/workflows/promote.yml) accepts all three images. Reviewer protection, payload/vulnerability checks and same-digest promotion remain mandatory. Optional full-acceptance evidence must match `image_name` and `image_digest` and cover complete streaming-stack checks. Operator-approved testing `latest` is not proof of full acceptance or authorization for an unattended host rollout.
