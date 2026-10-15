# Evidence and verification status

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

These findings explain the implementation choices. The ongoing final-image build, plugin checks, Intel encode probes and startup/shutdown tests must still pass before the runtime tasks are checked.

## Unfinished acceptance

No completed Wolf image, registry candidate, hardware encode result, Moonlight session or accepted `latest` is recorded yet. Session latency/quality, zero-copy behavior, audio, controls, Steam/Lutris integration and idle DRM release remain unverified. Hardware/deployment measurements belong outside this repository. The active change is not ready to archive.
