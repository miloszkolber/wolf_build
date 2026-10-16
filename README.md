# wolf_build

Intel-focused Wolf streaming runtime and minimal Steam/Heroic application builds, maintained from upstream sources and packages. Heroic starts in Console Mode for GOG-first TV use. Wolf starts on demand through the shared [llama_build gate](https://github.com/miloszkolber/llama_build/tree/master/cmd/gate).

**Status: ready for operator game/session acceptance.** Every successful default-channel build publishes an immutable input-hash tag and advances `latest` to that same checked digest. CI, payload/session probes and HIGH/CRITICAL scans are required. Intel H.264/HEVC/AV1 probes passed, but full game/session acceptance remains separate. See the [task ledger](openspec/changes/intel-wolf-runtime/tasks.md) and [evidence](openspec/changes/intel-wolf-runtime/evidence.md).

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

Use `GH_TOKEN` for authenticated upstream API discovery when needed. Never put it in manifests, image args or repository files. Resolution/API failure stops the candidate instead of selecting an unrecorded fallback. `.build/` holds generated manifests, sources and the Docker context. Do not commit it.

The lock resolves Wolf's `stable` branch, the latest patch in its compatible GStreamer series, Wolf's declared compositor pin, interpipe, an Intel media/VPL stack with its declared libva/GMM/dispatcher versions, source-level CMake dependencies, the Rust toolchain digest and the Ubuntu platform digest. Build sources are acquired by full Git object identity, including pinned submodules. This is not a claim that Git archives carry upstream SHA256 signatures. Cargo's lock verifies crate inputs.

Builder and runtime use Ubuntu's normal signed package repositories. Weekly cache invalidation captures package security updates without forcing a rebuild on every discovery run. The final image records distribution/build package versions and source/license inventories. Full input identity includes the packaging files, not only Wolf's upstream version. Package repositories are not frozen, so rebuilding a source lock can produce different package versions. Preserve the tested image digest for rollback, not a promise of bit-reproducible builds.

The runtime and [Steam/Heroic application images](compose/apps.md) are built separately here. No gate source, SYCL stack, NVIDIA CUDA/NVRTC runtime or application distribution is copied into the streaming runtime. Intel VA/VPL, required Mesa rendering, embedded audio, input integration and supported software fallback encoders are preserved. GStreamer plugins are explicitly selected, not reduced using `ldd` alone. Application images use their own small shared layer with amd64/i386 graphics and audio clients, not copies of upstream app Dockerfiles. Their daily workflow records dependencies and produces immutable candidates after smoke/SBOM/vulnerability checks. Lutris builds are retired.

## Run and accept

The [Compose example](compose/README.md) pins the published, device-free gate directly in YAML. Its environment file contains only the candidate image and host-specific device/group settings. Runtime creation is separate from startup. Production rollout is not part of a build.

An isolated Intel encode probe, without Docker authority or production state, can be run against a completed candidate:

```sh
docker run --rm --network none --device /dev/dri/renderD128 --entrypoint python3 -v "$PWD/scripts/test-intel.py:/test-intel.py:ro" wolf-candidate:local /test-intel.py
```

Choose the target device explicitly. This probes supported hardware encoders. It does not prove Wayland capture, zero-copy session behavior, Moonlight quality, audio, controllers or idle DRM release. Those require the [acceptance procedure](openspec/changes/intel-wolf-runtime/design.md#acceptance-and-recovery) and an operator-reviewed record.

## Maintain and publish

Runtime and application workflows check daily in UTC, on relevant changes, PRs and manual requests. New images require changed sources, shipped recipes, base/toolchain digests or selected distribution-package versions. Discovery resolves the exact dependency closure, including inherited base security updates, from signed repositories. Assembly installs those versions and verifies the installed closure. A changed date or unrelated repository update does not create an image. Steam and Heroic have separate identities, so a Heroic release does not rebuild Steam. Unchanged images are reused and freshly checked/scanned. Runtime provenance requires full Git history. The independent gate is not a runtime build input.

The workflow's build justification names changed input categories and package version deltas. Exact manifests, package locks, SBOM and scan results provide the evidence. Checks may report a newly disclosed vulnerability even when no fixed upstream package exists. That failure is not bypassed by producing an identical calendar-labelled image. Normal repositories may retire older versions, so a lock that is no longer available fails assembly and needs fresh discovery rather than silently floating to another version.

Only separate default-branch publication jobs can write packages. A shared publisher validates the checked image identity, preserves existing immutable tags and updates `latest` without rebuilding or changing the digest. Workflow serialization and a newer-publisher check prevent an old re-run from rolling `latest` back. Reusing an unchanged image still repairs a stale/missing `latest`. Explicit `wolf_sha` overrides publish versioned candidates only and do not change the default channel. There is no separate promotion workflow or approval step.

PRs use read-only package permissions on disposable hosted runners, never trusted GPU infrastructure. Failed checks leave `latest` unchanged. CI publishes SBOM/scan evidence and rejects immutable-tag identity collisions. Publication is not host rollout, and `latest` is not a claim of completed [game/session acceptance](openspec/acceptance.md).

[`openspec/`](openspec/README.md) owns scope, contracts, tasks and verification. Host paths, credentials, hardware measurements and deployment-specific reports stay outside this repository.
