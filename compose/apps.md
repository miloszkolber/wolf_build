# Steam and Heroic images

This repository builds `ghcr.io/<owner>/wolf_steam` and `ghcr.io/<owner>/wolf_heroic` from its own [Dockerfile](../docker/apps.Dockerfile). Successful default-channel checks automatically publish `latest`. Record resolved digests separately for deployment evidence. Lutris is retired and has no build target or scheduled publication.

## Payload and compatibility

Both targets use a digest-pinned Ubuntu 26.04 base, Gamescope/Xwayland, a small session D-Bus, non-root application processes and Mesa/ALSA/Pulse client libraries for amd64 and i386. The 32-bit libraries are required by Steam/Proton/Wine. PulseAudio's server remains in Wolf. There is no second audio container, desktop environment, panel, terminal, NVIDIA integration, Decky loader or copied upstream base-app image. Sway remains installed for explicit fallback and device-free CI session checks.

The default ALSA PCM and control use the Pulse plugin through `/etc/asound.conf`, respecting Wolf's `PULSE_SERVER`, `PULSE_SINK` and `PULSE_SOURCE`. Installing plugins alone does not select them as the default. Games must not fall back to a nonexistent host sound card. Publication checks real default-ALSA playback from both ABIs into an isolated session sink monitor. This is not proof of audio in every nested Steam runtime or game.

## Compositor selection

Gamescope is the default for both applications (`RUN_GAMESCOPE=1` in the image). Steam enables Gamescope's `-e` integration and runs through its Xwayland display, matching upstream's Steam compositor path. Heroic uses ordinary Gamescope composition. The launcher validates the requested binary before starting. Gamescope uses Wolf's `GAMESCOPE_WIDTH`, `GAMESCOPE_HEIGHT` and `GAMESCOPE_REFRESH` values and hides the cursor after three idle seconds. An explicitly empty `RUN_GAMESCOPE=` selects Sway for fallback or device-free probes.

Steam installs Ubuntu's `steam-installer` with no recommended packages. Valve's client, Proton and games update in the persistent user home, not in a fabricated immutable Steam-client version. Their runtime updates are outside the distribution package inventory. A container-private system bus and NetworkManager provide Big Picture's network-status API. The status daemon observes Docker's externally configured interface without NET_ADMIN/NET_RAW, leaves addresses/DNS unchanged and uses a real connectivity probe. No host system bus, host NetworkManager, Bluetooth daemon or desktop service is exposed.

Heroic resolves its latest stable amd64 `.deb` and checks the GitHub-published SHA256 during acquisition and assembly. It starts with `--console --fullscreen --no-sandbox` for GOG-first TV use; Chromium's user-namespace sandbox is disabled because supported hosts may restrict unprivileged namespaces, and the application container remains the isolation boundary and manages its own GE-Proton/UMU runners and game downloads in persistent user state. It does not install GOG Galaxy or a separate distribution Wine stack. No custom bubblewrap patch removes capability checks. App containers must not add `SYS_ADMIN` solely to bypass an upstream image assumption. User-namespace availability and the target host's security policy require explicit acceptance.

The build removes separate non-Intel Vulkan drivers and ICD registrations in the package-install layer and records every removed file. It keeps Mesa's shared Gallium/LLVM libraries because distro packaging shares them with Intel rendering. OpenGL software rendering remains available, but software/non-Intel Vulkan is intentionally excluded. The image smoke check verifies Intel Vulkan/DRI library closure and Pulse clients for both ABIs and rejects unwanted audio servers, Bluetooth daemons and build tooling.

## Build and dependency updates

Run Python in the development container, then Docker in the development Docker context:

```sh
python3 scripts/resolve-apps.py --app steam
bash scripts/resolve-packages.sh steam
python3 scripts/lock-packages.py steam > .build/apps.json
docker build -f docker/apps.Dockerfile --target steam --build-arg BASE_IMAGE="$(jq -r .inputs.base .build/apps.json)" --build-arg INPUT_SHA256="$(jq -r .input_sha256 .build/apps.json)" -t wolf-steam:local .
```

Use profile and target `heroic` for the second image. Package discovery uses Docker to simulate dependency selection in the immutable base, without GPU, production state or a mounted Docker socket. The common stage is shared locally. [Application CI](../.github/workflows/apps.yml) checks weekly (Monday), on source changes, PRs and dispatch. It selects actual package versions including base security upgrades. Only changed relevant inputs create a new image. The date is metadata, not a cache invalidator. Steam does not resolve Heroic releases or include them in its identity. Shared package roots in `docker/packages/` feed discovery, and generated exact locks feed assembly.

Each image embeds its resolved base/release/recipe/package manifest and installed package inventory. CI records image size, CycloneDX SBOM and HIGH/CRITICAL findings and tests non-default UID/GID plus nested sessions. Failed checks prevent publication. PRs cannot publish and input-hash tags are never overwritten. The published immutable tag is the 16-character identity hash, with no `candidate-` prefix. Assembly enforces the resolved package versions and closure; if a repository has retired a selected version, assembly fails rather than substituting it. Unchanged weekly discovery reuses and rescans the existing image, including a digest recovered through `latest` when the identity predates the tag naming, without manufacturing a new digest.

## Wolf integration

Wolf creates these application containers, not Compose. It supplies `PUID`, `PGID`, `XDG_RUNTIME_DIR`, `WAYLAND_DISPLAY`, Pulse server/sink/source, linked DRM/input devices, fake-udev and the per-user `/home/retro` mount. The entrypoint keeps those paths and groups, changes ownership only on top-level writable directories and the supplied session Wayland socket, then drops privileges before launching the application. It does not recursively rewrite game-library ownership. Nested Sway hides the cursor after inactivity and while typing for couch navigation; gamescope hides it after the same idle delay.

The pinned Wolf runner reads the current `hidraw` and `input` majors from `/proc/devices` and replaces the application's device-cgroup rules immediately before container creation. Keep saved `base_create_json.HostConfig.DeviceCgroupRules` consistent with the kernel as fallback if discovery fails, and check the actual container's effective grants when diagnosing input. Application containers are siblings, so they do not inherit runtime device grants.

The maintained runner references use unpinned `:latest` images and a Heroic runner name with a `heroic-games:/games:rw` shared library:

```toml
image = "ghcr.io/<owner>/wolf_steam:latest"
image = "ghcr.io/<owner>/wolf_heroic:latest"
```

Keep `start_virtual_compositor = true` and the Steam runner's existing name/home. Use a Heroic runner name and its own persistent home. Preserve retired homes/libraries as data rather than pretending their Wine prefixes and settings are a Heroic configuration. Do not silently weaken host user-namespace or sandbox policy to make a game launch. Steam accepts simple `STEAM_STARTUP_FLAGS` without shell evaluation. Both runners use Gamescope by default.

For de novo deployments, test both images with the exact Wolf runtime: first login/download, Steam/Proton and Heroic GOG games, 32/64-bit Intel rendering, sound, keyboard/mouse/controller including hotplug, library persistence, normal exit, reconnect and idle cleanup. Retain prior configuration and back up state first. Source checks and fake-app session probes do not establish this acceptance.

Successful default-branch builds automatically publish the checked immutable tag and the same digest as `latest`. No manual promotion is required. Reused images are rechecked, immutable tags are preserved and stale `latest` is repaired. [Full-acceptance evidence](../openspec/acceptance.md) remains a separate record of real streaming/game tests. Publishing `latest` is not a host rollout or a full-acceptance claim.
