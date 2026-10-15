# Evidence and verification status

## Application-image scope correction

The complete application workflow passed on source `060dca2` (Actions run `38755980934`): both builds, bounded final-image/session checks, zero HIGH/CRITICAL findings, SBOM creation and separate publication jobs. Read-only build permissions and the default-branch/non-PR publication guard were reviewed in the workflow. Registry manifests were readable anonymously and their full input identities matched CI evidence. The published Steam digest was additionally pulled anonymously and its final-image payload check passed. The large Lutris pull timed out during layer download, so verification used the anonymous registry manifest/config plus CI's exact-image smoke evidence rather than claiming a completed local pull.

| Public candidate | Published digest |
| --- | --- |
| `ghcr.io/miloszkolber/wolf_steam:candidate-54bdd4ad9b367169` | `sha256:d11afd56b77a55958839c52456cd2acffa88d5f518a9134c16e3b8e8731b2718` |
| `ghcr.io/miloszkolber/wolf_lutris:candidate-54bdd4ad9b367169` | `sha256:e784dc119ed40ea0bd7cd1b269b6fadec29776ffcee109dd2548913d214cd82d` |

These are unaccepted candidates, not `latest` promotions or deployment changes. Real Intel rendering, audio, controllers and game/session acceptance remain required.

Steam and Lutris are now explicit deliverables, not upstream-image references outside the repository. The implementation uses an independently authored common/Steam/Lutris Dockerfile on supported Ubuntu 26.04. It does not copy upstream Dockerfiles, inherit the upstream Ubuntu 25.04 base-app image, rebuild patched Xwayland/bubblewrap or import desktop, Decky, gamepad-AppImage or NVIDIA service layers. PulseAudio remains embedded in Wolf. Required i386 graphics/audio and Wine dependencies are retained rather than claiming minimality by removing game support.

The application resolver successfully acquired stable Lutris 0.5.22 using its upstream-published SHA256 and resolved the supported base digest. Daily application CI records recipe/base/release/refresh identity, installed package versions, SBOM, vulnerability results and image size. Candidate publication is separated from read-only PR builds. The existing protected promotion workflow now selects the repository and rejects application evidence without a matching repository name, exact digest and complete session checks.

Executed source checks after implementation: 27 Python tests, shell syntax for application scripts, 17 Markdown files with zero failures, strict OpenSpec validation (1 change) and actionlint. Resolver tests cover rejected prerelease/missing/unverified assets, all identity inputs, checksum failures preserving prior downloads and nested recipe changes. Promotion tests cover both application repositories and reject wrong-repository and incomplete controller evidence.

Both optimized application images built and passed final payload/Intel library closure, default/custom identity, rejected root-like IDs, real headless Sway/Xwayland fake-app sessions, two-run home persistence and normal shutdown checks. The actual Lutris version command also passed as the custom UID. The same static fake-udev executable extracted from the completed Wolf image ran successfully inside both application images. These tests did not launch real games or test hardware rendering/audio/controllers. The first Lutris build's root-version failure was corrected by probing as the application user with a disposable HOME. This prevents the check from baking UID-specific cache state into the image. The probe resolves the actual frontend executable on PATH instead of assuming its install directory.

Payload inspection identified distinct non-Intel Vulkan libraries separate from Intel's shared Gallium/LLVM closure. The revised recipe removes those Vulkan drivers and ICDs inside the install layer, preserves both Intel ABIs and logs each omitted file. Removed the unnecessary D-Bus systemd user-session package. SBOM/vulnerability publication and real Intel/game acceptance remain to be established. No production images, application config or game state were changed.

Lutris startup diagnostics identified concrete consumers for two small dependencies: `pciutils` for GPU detection and `python3-protobuf` for the Battle.net source. Both are now explicit rather than accepting silently disabled functionality under `--no-install-recommends`. Application-only source pushes are excluded from the separate runtime workflow to avoid unrelated full source builds.

## Successful runtime image and isolated checks

The simplified runtime built successfully. A separate network-isolated final-image run passed library/plugin/license checks. An isolated Intel VA probe passed H.264, HEVC and AV1 encode pipelines. This proves hardware encoder availability and basic operation, not zero-copy capture, game quality or Moonlight acceptance. Hardware-specific details and measurements remain in the deployment owner's local evidence.

The exact published gate controlled a uniquely named test runtime in a separate network namespace, with temporary container-owned state and no production ports or game state. Health returned successfully without starting the runtime. A cold `/serverinfo` request started Wolf and returned successfully. Docker health and configured TCP listeners became ready. Idle expiry stopped Wolf and PulseAudio cleanly with exit status zero, and gate reacquired its listeners. Expected isolation diagnostics included unavailable Docker inspection inside the socket-free runtime and unavailable mDNS multicast. No application-container launch, full UDP client exchange or real session was inferred from this check.

The first runtime vulnerability gate correctly failed on three HIGH Go-stdlib advisories in `/usr/bin/pebble`, an unowned executable bundled in the Ubuntu base, not used by Wolf's Supervisor or the application's tini entrypoint. The build now omits that unused service manager and static checks reject its return. Application scans subsequently found one HIGH `CVE-2026-84782` in an inherited `openssl-provider-legacy` package, with an Ubuntu fix available. CI failed at the same gate rather than publishing. The application common stage now upgrades inherited packages before installing application dependencies. This closes the gap where `apt-get install` updated required packages but left an unrelated base package stale. All three final local images generated SBOMs and passed HIGH/CRITICAL scans with zero findings after the repairs. Application static, identity, fake-udev and two-run headless persistence/session checks passed again. No blanket suppression or vulnerability exception was added.

## Simplification review

The earlier snapshot approach described below is superseded. Timestamped snapshot discovery changed the input hash on every run even without upstream changes, and snapshot downloads repeatedly returned HTTP 500/502. The build now uses normal signed Ubuntu repositories with the existing weekly refresh identity. Removed snapshot discovery, generated arguments, workflow plumbing and Rust-image CA bootstrapping. Retained Ubuntu because the selected source stack already compiled on it. A distro port would add unverified changes rather than remove required components. Rebuilding a lock is not package-reproducible. The tested image digest remains the rollback identity.

Compose now pins the accepted shared gate digest, container names, protocol settings, standard Docker socket and relative state mounts directly in YAML. `.env.example` shrank from 27 to 8 lines and contains only the candidate image and device/group settings. Removed blanket `env_file` injection into both services. Image defaults supply runtime logging, Intel driver and shutdown settings. The unaccepted `latest` example is replaced by an explicit digest placeholder.

Source checks after simplification passed: 22 Python tests, 15 Markdown files with zero failures, strict OpenSpec validation (1 item), actionlint and Compose configuration with the runtime profile. The lock fixture now proves different discovery days in the same week keep the identity unchanged and the next week changes it. Rendered Compose retains required handoff settings, matching gate/runtime names, device mappings and fixed socket mounts without leaking the host-selection variables into container environments.

Earlier runtime checks found missing quadmath and Wayland cursor/EGL libraries after successful source compilation. Runtime packages now include those libraries, and the static checker aggregates missing dependencies instead of hiding all but the first. A completed final-image/plugin check is still required. No production deployment or session acceptance is claimed.

## Current state

Gate and application candidates are published. Wolf, Steam and Lutris images have built and passed their bounded checks and local security scans described above. Runtime registry publication verification and complete game/session acceptance are still open. Do not infer acceptance from source delivery or isolated smoke checks. No production deployment or pairing state has been changed.

The repository was initially private, where GitHub rejected required-reviewer protection. The operator subsequently authorized public visibility. The repository is now public and `intel-acceptance` has required-reviewer protection and a main-branch deployment policy. The guard was preserved rather than bypassed. This enables protected promotion but is not session acceptance or permission to promote an untested image.

## Delivered and checked boundaries

- Gate PR 4 was reviewed, repaired, merged and published in `llama_build`. Its archived change owner is `openspec/changes/archive/2026-10-15-universal-env-gate/` in that repository.
- Published gate `816b5f152e99` has digest `sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40`. Its extracted executable passed both profile traffic tests against mock Docker HTTP and real runtime TCP sockets. A read-only/network-isolated image health check passed. This is not Moonlight acceptance.
- Wolf source discovery resolves the `stable` branch, the latest compatible GStreamer patch (currently `1.26.11`), Wolf's declared compositor pin, interpipe, the Intel `26.3.5` media/VPL pair and its declared libva/GMM/dispatcher sources, CMake source dependencies and pinned Rust/base images. Signed distribution packages use normal repositories, not timestamped snapshots.
- Acquisition checked out the full selected Git objects and pinned submodules, retained source licenses and generated a version 2 Docker context. No upstream-signed archive checksum is fabricated. Dirty source caches and stale packaging identity are rejected.
- The development-container unit suite passed `27` tests. Coverage includes source/input identity, incompatible dependency sets, missing releases, prereleases, rate limits, legitimate submodule updates, cache edits/object mismatch, checked application downloads and acceptance records rejecting CPU-only smoke evidence, incomplete checks, wrong repositories/digests and software fallback.
- Repository documentation checks passed for `17` Markdown files. Strict OpenSpec `1.14.1` validation passed for the active change. Workflow validation with `actionlint 1.7.12` passed. The full Compose configuration, including its runtime profile, validated without creating or starting service containers.
- An isolated loopback registry fixture verified that `imagetools create --prefer-index=false` preserves the exact digest through candidate, accepted and latest tags. This used the tiny gate image as a fixture, not a Wolf release or acceptance record. Digest extraction uses descriptor JSON and `jq`, not an unsupported scalar formatting assumption.

## Build bring-up findings

The first supported-base builds established the need for explicit XCB development dependencies in libva. Intel's media-driver build treats a GCC 15 array-bounds diagnostic as an error, so the CMake build selects Clang without disabling the warning gate. Clang is explicitly paired with the default GCC standard-library installation to avoid selecting a partially installed alternate GCC directory.

The early snapshot recipe needed a copied Rust-image CA bundle and explicit APT trust path. Normal signed Ubuntu repositories replaced that extra bootstrap layer after the simplification review. APT index failures remain fatal instead of appearing later as missing packages.

Wolf's `moonlight-server` target requires ICU (`find_package(ICU 61.0 COMPONENTS uc)` via the Boost locale path), but the build image carried only the `libicu78` runtime library. Both the local and CI builds failed deterministically at Wolf configure with `Failed to find all ICU components (missing: ICU_INCLUDE_DIR ICU_LIBRARY uc)`. Commit `8132fb1` adds `libicu-dev` plus `libzstd-dev`/`zlib1g-dev` for the external dwarf/zstd metadata path, without disabling input support.

With configure fixed, the Wolf compile exposed a prefix-path gap: Wolf includes GStreamer as `<gstreamer-1.0/gst/...>`, which resolves through the compiler default `/usr/local/include` path in the upstream layout. Our `/opt/wolf-runtime` prefix is not on the default path, so commit `9ceeb19` exports `C_INCLUDE_PATH`/`CPLUS_INCLUDE_PATH` in the build stage. `pkg-config` already supplies the suffixed `gstreamer-1.0` directory. This adds the prefix directory and subsequent local image/static checks passed.

These findings explain the implementation choices. The successful image, plugin, isolated Intel encode and startup/shutdown checks above support the completed runtime tasks, not complete Moonlight acceptance.

## Unfinished acceptance

Runtime registry publication, full Moonlight sessions and accepted `latest` remain open. Session latency/quality, zero-copy behavior, real audio, controls, Steam/Lutris game integration and idle DRM release remain unverified. Hardware/deployment measurements belong outside this repository. The active change is not ready to archive.
