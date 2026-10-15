# Evidence and verification status

## Application-image scope correction

Steam and Lutris are now explicit deliverables, not upstream-image references outside the repository. The implementation uses an independently authored common/Steam/Lutris Dockerfile on supported Ubuntu 26.04. It does not copy upstream Dockerfiles, inherit the upstream Ubuntu 25.04 base-app image, rebuild patched Xwayland/bubblewrap or import desktop, Decky, gamepad-AppImage or NVIDIA service layers. PulseAudio remains embedded in Wolf. Required i386 graphics/audio and Wine dependencies are retained rather than claiming minimality by removing game support.

The application resolver successfully acquired stable Lutris 0.5.22 using its upstream-published SHA256 and resolved the supported base digest. Daily application CI records recipe/base/release/refresh identity, installed package versions, SBOM, vulnerability results and image size. Candidate publication is separated from read-only PR builds. The existing protected promotion workflow now selects the repository and rejects application evidence without a matching repository name, exact digest and complete session checks.

Executed source checks after implementation: 27 Python tests, shell syntax for application scripts, 17 Markdown files with zero failures, strict OpenSpec validation (1 change) and actionlint. Resolver tests cover rejected prerelease/missing/unverified assets, all identity inputs, checksum failures preserving prior downloads and nested recipe changes. Promotion tests cover both application repositories and reject wrong-repository and incomplete controller evidence.

The first Steam image built and passed payload, Intel library presence and custom/default identity checks. A separate isolated probe used real headless Sway/Xwayland with a fake Steam executable and verified X display access, Pulse environment forwarding, custom non-root identity and clean session exit. It did not launch Steam or test audio/GPU/games. The first Lutris build reached its final smoke check, where calling `lutris --version` as root attempted a GTK warning dialog without a display. The check now runs the command as the application user. Rebuild verification is pending.

Payload inspection identified distinct non-Intel Vulkan libraries separate from Intel's shared Gallium/LLVM closure. The revised recipe removes those Vulkan drivers and ICDs inside the install layer, preserves both Intel ABIs and logs each omitted file. Removed the unnecessary D-Bus systemd user-session package. Final optimized image size, smoke, two-run persistence/session probes, SBOM/vulnerability publication and real Intel/game acceptance remain to be established. No production images, application config or game state were changed.

## Simplification review

The earlier snapshot approach described below is superseded. Timestamped snapshot discovery changed the input hash on every run even without upstream changes, and snapshot downloads repeatedly returned HTTP 500/502. The build now uses normal signed Ubuntu repositories with the existing weekly refresh identity. Removed snapshot discovery, generated arguments, workflow plumbing and Rust-image CA bootstrapping. Retained Ubuntu because the selected source stack already compiled on it. A distro port would add unverified changes rather than remove required components. Rebuilding a lock is not package-reproducible. The tested image digest remains the rollback identity.

Compose now pins the accepted shared gate digest, container names, protocol settings, standard Docker socket and relative state mounts directly in YAML. `.env.example` shrank from 27 to 8 lines and contains only the candidate image and device/group settings. Removed blanket `env_file` injection into both services. Image defaults supply runtime logging, Intel driver and shutdown settings. The unaccepted `latest` example is replaced by an explicit digest placeholder.

Source checks after simplification passed: 22 Python tests, 15 Markdown files with zero failures, strict OpenSpec validation (1 item), actionlint and Compose configuration with the runtime profile. The lock fixture now proves different discovery days in the same week keep the identity unchanged and the next week changes it. Rendered Compose retains required handoff settings, matching gate/runtime names, device mappings and fixed socket mounts without leaking the host-selection variables into container environments.

Earlier runtime checks found missing quadmath and Wayland cursor/EGL libraries after successful source compilation. Runtime packages now include those libraries, and the static checker aggregates missing dependencies instead of hiding all but the first. A completed final-image/plugin check is still required. No production deployment or session acceptance is claimed.

## Current state

Gate is complete and published. Wolf implementation is present but final-image bring-up is still in progress. Do not infer runtime or session acceptance from source delivery. No production deployment or pairing state has been changed.

The repository was initially private, where GitHub rejected required-reviewer protection. The operator subsequently authorized public visibility. The repository is now public and `intel-acceptance` has required-reviewer protection and a main-branch deployment policy. The guard was preserved rather than bypassed. This enables protected promotion but is not session acceptance or permission to promote an untested image.

## Delivered and checked boundaries

- Gate PR 4 was reviewed, repaired, merged and published in `llama_build`. Its archived change owner is `openspec/changes/archive/2026-10-15-universal-env-gate/` in that repository.
- Published gate `816b5f152e99` has digest `sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40`. Its extracted executable passed both profile traffic tests against mock Docker HTTP and real runtime TCP sockets. A read-only/network-isolated image health check passed. This is not Moonlight acceptance.
- Wolf source discovery resolves the `stable` branch, the latest compatible GStreamer patch (currently `1.26.11`), Wolf's declared compositor pin, interpipe, the Intel `26.3.5` media/VPL pair and its declared libva/GMM/dispatcher sources, CMake source dependencies, pinned Rust/base images and a signed Ubuntu repository snapshot.
- Acquisition checked out the full selected Git objects and pinned submodules, retained source licenses and generated a version 2 Docker context. No upstream-signed archive checksum is fabricated. Dirty source caches and stale packaging identity are rejected.
- The development-container unit suite passed `22` tests. Coverage includes source/input identity, incompatible dependency sets, missing releases, prereleases, rate limits, legitimate submodule updates, cache edits/object mismatch and acceptance records rejecting CPU-only smoke evidence, incomplete checks, wrong digests and software fallback.
- Repository documentation checks passed for `15` Markdown files. Strict OpenSpec `1.14.1` validation passed for the active change. Workflow validation with `actionlint 1.7.12` passed. The full Compose configuration, including its runtime profile, validated without creating or starting service containers.
- An isolated loopback registry fixture verified that `imagetools create --prefer-index=false` preserves the exact digest through candidate, accepted and latest tags. This used the tiny gate image as a fixture, not a Wolf release or acceptance record. Digest extraction uses descriptor JSON and `jq`, not an unsupported scalar formatting assumption.

## Build bring-up findings

The first supported-base builds established the need for explicit XCB development dependencies in libva. Intel's media-driver build treats a GCC 15 array-bounds diagnostic as an error, so the CMake build selects Clang without disabling the warning gate. Clang is explicitly paired with the default GCC standard-library installation to avoid selecting a partially installed alternate GCC directory.

Ubuntu's minimal base does not initially provide a usable default TLS trust path for snapshot bootstrapping. The build copies the CA bundle from the pinned Rust image and passes its path explicitly to APT, retaining certificate and repository-signature verification. A fresh snapshot-index diagnostic succeeded. APT index failures are fatal instead of appearing later as missing packages.

Wolf's `moonlight-server` target requires ICU (`find_package(ICU 61.0 COMPONENTS uc)` via the Boost locale path), but the build image carried only the `libicu78` runtime library. Both the local and CI builds failed deterministically at Wolf configure with `Failed to find all ICU components (missing: ICU_INCLUDE_DIR ICU_LIBRARY uc)`. Commit `8132fb1` adds `libicu-dev` plus `libzstd-dev`/`zlib1g-dev` for the external dwarf/zstd metadata path, without disabling input support.

With configure fixed, the Wolf compile exposed a prefix-path gap: Wolf includes GStreamer as `<gstreamer-1.0/gst/...>`, which resolves through the compiler default `/usr/local/include` path in the upstream layout. Our `/opt/wolf-runtime` prefix is not on the default path, so commit `9ceeb19` exports `C_INCLUDE_PATH`/`CPLUS_INCLUDE_PATH` in the build stage. `pkg-config` already supplies the suffixed `gstreamer-1.0` directory; this adds the prefix directory. CI rerun and a local rebuild are in progress; neither has produced a verified image yet.

These findings explain the implementation choices. The ongoing final-image build, plugin checks, Intel encode probes and startup/shutdown tests must still pass before the runtime tasks are checked.

## Unfinished acceptance

No completed Wolf image, registry candidate, hardware encode result, Moonlight session or accepted `latest` is recorded yet. Session latency/quality, zero-copy behavior, audio, controls, Steam/Lutris integration and idle DRM release remain unverified. Hardware/deployment measurements belong outside this repository. The active change is not ready to archive.
