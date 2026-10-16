# Steam and Heroic images

This repository builds `ghcr.io/<owner>/wolf_steam` and `ghcr.io/<owner>/wolf_heroic` from its own [Dockerfile](../docker/apps.Dockerfile). Successful default-channel checks automatically publish `latest`. Record resolved digests separately for deployment evidence and rollback. Lutris is retired and has no build target or scheduled publication.

## Payload and compatibility

Both targets use a digest-pinned Ubuntu 26.04 base, package-managed Sway/Xwayland, a small session D-Bus, non-root application processes and Mesa/ALSA/Pulse client libraries for amd64 and i386. The 32-bit libraries are required by Steam/Proton/Wine. PulseAudio's server remains in Wolf. There is no second audio container, desktop environment, panel, terminal, NVIDIA integration, Decky loader, gamescope build or copied upstream base-app image.

Steam installs Ubuntu's `steam-installer` with no recommended packages. Valve's client, Proton and games update in the persistent user home, not in a fabricated immutable Steam-client version. Their runtime updates are outside the distribution package inventory. A container-private system bus and NetworkManager provide Big Picture's network-status API. The status daemon observes Docker's externally configured interface without NET_ADMIN/NET_RAW, leaves addresses/DNS unchanged and uses a real connectivity probe. No host system bus, host NetworkManager, Bluetooth daemon or desktop service is exposed.

Heroic resolves its latest stable amd64 `.deb` and checks the GitHub-published SHA256 during acquisition and assembly. It starts with `--console --fullscreen` for GOG-first TV use and manages its own GE-Proton/UMU runners and game downloads in persistent user state. It does not install GOG Galaxy or a separate distribution Wine stack. No custom bubblewrap patch removes capability checks. App containers must not add `SYS_ADMIN` solely to bypass an upstream image assumption. User-namespace availability and the target host's security policy require explicit acceptance.

The build removes separate non-Intel Vulkan drivers and ICD registrations in the package-install layer and records every removed file. It keeps Mesa's shared Gallium/LLVM libraries because distro packaging shares them with Intel rendering. OpenGL software rendering remains available, but software/non-Intel Vulkan is intentionally excluded. The image smoke check verifies Intel Vulkan/DRI library closure and Pulse clients for both ABIs and rejects unwanted audio servers, Bluetooth daemons and build tooling. Steam's private network-status service has an evidenced UI consumer. Further pruning requires closure and game tests, not package-name heuristics.

## Build and dependency updates

Run Python in the development container, then Docker in the development Docker context:

```sh
python3 scripts/resolve-apps.py > .build/apps.json
docker build -f docker/apps.Dockerfile --target steam --build-arg BASE_IMAGE="$(jq -r .inputs.base .build/apps.json)" --build-arg REFRESH="$(jq -r .inputs.refresh .build/apps.json)" --build-arg INPUT_SHA256="$(jq -r .input_sha256 .build/apps.json)" -t wolf-steam:local .
```

Use target `heroic` for the second image. No GPU, Docker socket or production state is needed to build either target. The common stage is shared locally. [Application CI](../.github/workflows/apps.yml) runs daily, on application-source changes, PRs and manual dispatch. Daily cache invalidation upgrades packages inherited from the base as well as installing current application dependencies, even without a new Heroic release. There is no snapshot-mirror or distro-port maintenance layer.

Each image embeds the resolved base/release/recipe/refresh manifest, the exact installed package versions and package copyright files. CI records image size, CycloneDX SBOM and HIGH/CRITICAL vulnerability findings. It tests non-default UID/GID setup without devices/network. Failed checks prevent candidate publication. PRs cannot publish. Input-hash candidate tags are never overwritten. Installed packages are recorded, not claimed frozen for a later rebuild. Preserve the original tested digest for rollback.

## Wolf integration

Wolf creates these application containers, not Compose. It supplies `PUID`, `PGID`, `XDG_RUNTIME_DIR`, `WAYLAND_DISPLAY`, Pulse server/sink/source, linked DRM/input devices, fake-udev and the per-user `/home/retro` mount. The entrypoint keeps those paths and groups, changes ownership only on top-level writable directories and the supplied session Wayland socket, then drops privileges before launching the application. It does not recursively rewrite game-library ownership. Nested Sway hides the cursor after inactivity and while typing for couch navigation.

During an authorized idle rollout, preserve existing games and pairing. Replace the retired Lutris entry with Heroic and use the maintained image references:

```toml
# In the existing Steam runner:
image = "ghcr.io/<owner>/wolf_steam:latest"
# In the Heroic runner:
image = "ghcr.io/<owner>/wolf_heroic:latest"
```

Keep `start_virtual_compositor = true` and the Steam runner's existing name/home. Use a Heroic runner name and its own persistent home. Preserve retired Lutris homes/libraries as data rather than pretending their Wine prefixes and settings are a Heroic configuration. Existing games can be explicitly imported from a preserved shared library. Remove NVIDIA-only device requests for the Intel target. The custom images do not need a `SYS_ADMIN` grant. Do not silently weaken host user-namespace or sandbox policy to make a game launch. Steam accepts simple `STEAM_STARTUP_FLAGS` without shell evaluation. These images always use nested Sway. Gamescope-only settings and Decky/SteamOS integration are not implemented.

For full acceptance, test both images with the exact Wolf runtime: first login/download, Steam/Proton and Heroic GOG games, 32/64-bit Intel rendering, sound, keyboard/mouse/controller including hotplug, library persistence, normal exit, reconnect and idle cleanup. Retain prior configuration and back up state. Source checks and fake-app session probes do not establish this acceptance.

Successful default-branch builds automatically publish the checked immutable tag and the same digest as `latest`. No manual promotion is required. Reused images are rechecked, immutable tags are preserved and stale `latest` is repaired. [Full-acceptance evidence](../openspec/acceptance.md) remains a separate record of real streaming/game tests. Publishing `latest` is not a host rollout or a full-acceptance claim.
