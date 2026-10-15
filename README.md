# wolf_build

Intel-focused Wolf streaming runtime and minimal Steam/Lutris application builds, maintained from upstream sources and packages. Wolf starts on demand through the shared [llama_build gate](https://github.com/miloszkolber/llama_build/tree/master/cmd/gate).

**Status: candidate verification in progress.** Gate is published and independently tested. Wolf, Steam and Lutris images have built and passed bounded payload/isolated checks. Wolf's isolated Intel encode and gate cold-request/idle-stop probes passed. Security-repaired final scans and full game/session acceptance remain open. No accepted `latest` or production rollout is established. See the [task ledger](openspec/changes/intel-wolf-runtime/tasks.md) and [actual evidence](openspec/changes/intel-wolf-runtime/evidence.md).

## Build

Run Python/Bun commands in the development container. Run Docker commands against the development Docker context. Do not install development tooling on the host.

```sh
python3 -m unittest discover -s tests
bun scripts/check-docs.mjs
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.14.1 validate --all --strict
python3 scripts/resolve.py --lock --gate-tag 816b5f152e99 --gate-digest sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40
python3 scripts/build-inputs.py
bash scripts/build.sh
docker run --rm --network none --entrypoint python3 wolf-candidate:local /app/check-runtime.py --static
```

Use `GH_TOKEN` for authenticated upstream API discovery when needed. Never put it in manifests, image args or repository files. Resolution/API failure stops the candidate instead of selecting an unrecorded fallback. `.build/` holds generated manifests, sources and the Docker context. Do not commit it.

The lock resolves Wolf's `stable` branch, the latest patch in its compatible GStreamer series, Wolf's declared compositor pin, interpipe, an Intel media/VPL stack with its declared libva/GMM/dispatcher versions, source-level CMake dependencies, the Rust toolchain digest and the Ubuntu platform digest. Build sources are acquired by full Git object identity, including pinned submodules. This is not a claim that Git archives carry upstream SHA256 signatures. Cargo's lock verifies crate inputs.

Builder and runtime use Ubuntu's normal signed package repositories. Weekly cache invalidation captures package security updates without forcing a rebuild on every discovery run. The final image records distribution/build package versions and source/license inventories. Full input identity includes the packaging files, not only Wolf's upstream version. Package repositories are not frozen, so rebuilding a source lock can produce different package versions. Preserve the tested image digest for rollback, not a promise of bit-reproducible builds.

The runtime and [Steam/Lutris application images](compose/apps.md) are built separately here. No gate source, SYCL stack, NVIDIA CUDA/NVRTC runtime or application distribution is copied into the streaming runtime. Intel VA/VPL, required Mesa rendering, embedded audio, input integration and supported software fallback encoders are preserved. GStreamer plugins are explicitly selected, not reduced using `ldd` alone. Application images use their own small shared layer with amd64/i386 graphics and audio clients, not copies of upstream app Dockerfiles. Their daily workflow records dependencies and produces immutable candidates after smoke/SBOM/vulnerability checks.

## Run and accept

The [Compose example](compose/README.md) pins the published, device-free gate directly in YAML. Its environment file contains only the candidate image and host-specific device/group settings. Runtime creation is separate from startup. Production rollout is not part of a build.

An isolated Intel encode probe, without Docker authority or production state, can be run against a completed candidate:

```sh
docker run --rm --network none --device /dev/dri/renderD128 --entrypoint python3 -v "$PWD/scripts/test-intel.py:/test-intel.py:ro" wolf-candidate:local /test-intel.py
```

Choose the target device explicitly. This probes supported hardware encoders. It does not prove Wayland capture, zero-copy session behavior, Moonlight quality, audio, controllers or idle DRM release. Those require the [acceptance procedure](openspec/changes/intel-wolf-runtime/design.md#acceptance-and-recovery) and an operator-reviewed record.

## Maintain and publish

The candidate workflow runs daily in UTC and on pushes, PRs and manual requests. Set repository variables `GATE_TAG` and `GATE_DIGEST` to an accepted shared-gate version before enabling registry publication. Build once, run final-image/plugin checks, produce a CycloneDX SBOM and fail on HIGH/CRITICAL vulnerabilities. No blanket vulnerability suppression is configured. Changed candidates receive immutable input-hash tags. The same tag is never overwritten with a conflicting full input identity.

PR build jobs have read-only package permissions and use disposable hosted runners, not trusted Docker/GPU infrastructure. Only a separate default-branch publication job receives package write authority. Candidate publication never advances `latest`.

The manual promotion workflow requires an `intel-acceptance` environment with required reviewers, an exact candidate digest and matching external acceptance evidence. Without those controls and successful session/codec evidence it fails closed. It tests digest-preserving staging before changing `latest` and retains accepted digest tags. See [promotion record format](openspec/acceptance.md).

[`openspec/`](openspec/README.md) owns scope, contracts, tasks and verification. Host paths, credentials, hardware measurements and deployment-specific reports stay outside this repository.
