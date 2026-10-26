# wolf_build

Intel-focused Wolf streaming runtime and minimal Steam/Heroic application builds, maintained from upstream sources and packages. Heroic starts in Console Mode for GOG-first TV use. Wolf starts on demand through the shared [llama_build gate](https://github.com/miloszkolber/llama_build/tree/master/cmd/gate).

## Build

Run Python/Bun commands in the development container. Run Docker commands against the development Docker context. Do not install development tooling on the host.

```sh
python3 -m unittest discover -s tests
bun scripts/check-docs.mjs
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.14.1 validate --all --strict
python3 scripts/resolve.py --lock
bash scripts/resolve-packages.sh runtime
python3 scripts/lock-packages.py runtime
python3 scripts/build-inputs.py
bash scripts/build.sh
docker run --rm --network none --entrypoint python3 wolf-candidate:local /app/check-runtime.py --static
```

Use `GH_TOKEN` for authenticated upstream API discovery when needed. Never put it in manifests, image args or repository files. Resolution/API failure stops the build instead of selecting an unrecorded fallback. `.build/` holds generated manifests, sources and the Docker context. Do not commit it.

The lock resolves Wolf's source release channel, the latest patch in its compatible GStreamer series, Wolf's declared compositor pin, interpipe, an Intel media/VPL stack with its declared libva/GMM/dispatcher versions, source-level CMake dependencies, the Rust toolchain digest and the Ubuntu platform digest. Discovery currently holds Wolf at its last reviewed commit because upstream's migrated `stable` channel has no published calendar release yet; the reviewed identity and the review trigger are recorded in [openspec/maintenance-state.md](openspec/maintenance-state.md). Build sources are acquired by full Git object identity, including pinned submodules. Cargo's lock verifies crate inputs.

GStreamer has an explicit reviewed 1.28-series override because the held Wolf source declares the unmaintained 1.26 line. The manifest records the declaration, selected series, review date, advisory cutoff, minimum fixed version and reason. Resolution rejects a selected patch below that floor or incomplete review metadata. Final-image checks verify the loaded GStreamer version, not just the presence of distribution packages. The distribution vulnerability scan does not cover the overriding source-built media stack, so [source advisory review](openspec/changes/gstreamer-1.28-series/evidence.md) remains necessary.

Builder and runtime use Ubuntu's normal signed package repositories. Discovery resolves the exact selected package closure, including inherited base security updates, and assembly installs those exact versions and verifies the installed inventory. Package repositories are not frozen, so rebuilding a source lock can produce different package versions. Preserve the tested image digest for rollback, not a promise of bit-reproducible builds.

The runtime and [Steam/Heroic application images](compose/apps.md) are built separately here. No gate source, SYCL stack, NVIDIA CUDA/NVRTC runtime or application distribution is copied into the streaming runtime. Intel VA/VPL, required Mesa rendering, embedded audio, input integration and supported software fallback encoders are preserved. GStreamer plugins are explicitly selected, not reduced using `ldd` alone. Application images use their own small shared layer with amd64/i386 graphics and audio clients, not copies of upstream app Dockerfiles.

## Run and accept

The [Compose example](compose/README.md) pins the published, device-free gate directly in YAML. Its environment file contains only the runner image and host-specific device/group settings. Runtime creation is separate from startup. Production rollout is not part of a build. Wolf stops a session after 900 seconds without a client (`WOLF_SESSION_IDLE_TIMEOUT`, `0` disables it), so a client that disappears ends the application container instead of leaving it running.

An isolated Intel encode probe, without Docker authority or production state, can be run against a completed build:

```sh
docker run --rm --network none --device /dev/dri/renderD128 --entrypoint python3 -v "$PWD/scripts/test-intel.py:/test-intel.py:ro" wolf-candidate:local /test-intel.py
```

Choose the target device explicitly. This probes supported hardware encoders. It does not prove Wayland capture, zero-copy session behavior, Moonlight quality, audio, controllers or idle DRM release. Those require the [acceptance procedure](openspec/changes/archive/2026-10-16-intel-wolf-runtime/design.md#acceptance-and-recovery) and an operator-reviewed record.

## Maintain and publish

The runtime workflow checks daily and the application workflow checks weekly (Monday) in UTC, on relevant changes, PRs and manual requests. New images require changed sources, shipped recipes, base/toolchain digests or selected distribution-package versions. A changed date or unrelated repository update does not create an image. Steam and Heroic have separate identities, so a Heroic release does not rebuild Steam. Unchanged images are reused and freshly checked/scanned. Runtime provenance requires full Git history. The independent gate is not a runtime build input. [openspec/maintenance-state.md](openspec/maintenance-state.md) owns the per-source reviewed revisions of the scheduled dependency review.

The build justification names changed input categories and package version deltas alongside the exact manifest, package locks, SBOM and scan results. If a repository has retired a selected version, assembly fails and needs fresh discovery rather than silently floating to another version.

Submodule identity contains only sorted paths and full commits, not local branch/tag descriptions. Component sources enter the runtime build immediately before their existing compile phases so a Wolf-only change does not rebuild the Intel libraries. The installed VA driver is stripped in the builder before final image assembly. Scans share one freshly updated database per job, retry transient download failures a bounded number of times and still fail closed if refresh or vulnerability checks fail.

Successful default-channel builds publish the identity as an immutable tag and the same digest as `latest`; there is no promotion workflow or approval step. A shared publisher validates the checked image identity, preserves existing immutable tags and updates `latest`. Workflow serialization and a newer-publisher check prevent an old re-run from rolling `latest` back, and reusing an unchanged image repairs a stale/missing `latest`. `wolf_sha` overrides publish versioned tags only. PRs use read-only package permissions on disposable hosted runners. Failed checks leave `latest` unchanged. Publication is not host rollout, and `latest` is not a claim of completed [game/session acceptance](openspec/acceptance.md).

[`openspec/`](openspec/README.md) owns scope, contracts, tasks and verification. Host paths, credentials, hardware measurements and deployment-specific reports stay outside this repository.
