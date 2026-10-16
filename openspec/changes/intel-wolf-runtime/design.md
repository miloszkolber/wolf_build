# Runtime and maintenance design

## Image boundary

Build `wolf_runtime`, `wolf_steam` and `wolf_lutris` here. Consume the gate owner’s published image without copying its source. Use `linux/amd64` and a supported distribution runtime initially. Upstream Wolf already uses multi-stage builds, so the improvement is controlled runtime contents and current compatible inputs, not adding a builder stage alone.

Keep upstream Wolf, `gst-wayland-display`, `gst-interpipe`, GStreamer, embedded PulseAudio and fake-udev. Preserve upstream's Supervisor/startup behavior in the first slice. The current upstream audio path is embedded, so do not introduce a separate PulseAudio image or a legacy sidecar-image update requirement.

Use the Intel iHD media driver, libva, VPL dispatcher/GPU runtime, matched GMM where needed, libdrm and the Intel Mesa EGL/GBM/OpenGL components required by the compositor and application integration. Kernel drivers and firmware remain host responsibilities. Do not include oneAPI compiler, Level Zero or SYCL packages merely because the comparison repository uses them.

## Dependency ownership and upstream resolution

| Input | Discovery owner | Resolution and compatibility policy |
| --- | --- | --- |
| Wolf | `games-on-whales/wolf` stable release channel | Resolve stable tag to full source commit. If no usable release metadata exists, resolve the published stable image's source revision after verifying provenance. Do not silently switch to development HEAD. |
| GStreamer | Upstream GStreamer tags/releases | Begin with Wolf's declared compatible series. Test newer stable series as candidates rather than assuming ABI compatibility. |
| Compositor and interpipe | Wolf source references and component upstreams | Honor Wolf's pinned compatible revisions initially. Discover newer releases/commits, but advance pins only after integration acceptance. An unversioned moving HEAD is not a resolved input. |
| Intel media driver and VPL GPU runtime | Intel release metadata | Resolve a supported, compatible release pair and its required GMM/libva constraints. Verify acquired assets or build exact source commits. |
| VPL dispatcher, libva, GMM | Component release metadata and dependency declarations | Resolve constraints from the selected Intel stack. Record all revisions and verification material. |
| Mesa/libdrm and system libraries | Supported distribution repositories | Prefer supported package versions and security updates. Evaluate an upstream Mesa build only for a demonstrated compatibility gap. |
| Distribution base | Official supported image | Resolve the selected tag to a platform digest. Maintenance can advance the digest, not silently change distribution release. |
| Shared gate | `llama_build` published version/digest | Resolve an image containing the environment-only profile contract. Test the consuming boundary and retain its digest independently of Wolf. |
| Actions | Dependabot (grouped) and reviewed updates | Pin third-party actions to SHAs with version comments, matching the sibling repositories. Validate new pipeline dependencies before publication. Base/toolchain digests are resolved daily by the input owner, not duplicated as Dockerfile fallbacks, so no docker Dependabot ecosystem applies. |

Resolver output is a machine-readable manifest in `.build/`, uploaded with each build and embedded in the image's provenance/licenses directory. It records source URLs, tags/full commits, base and gate digests, package versions, compatibility constraints, checksums and checksum/signature provenance. Locally computed hashes identify bytes but are not falsely presented as upstream authenticity proofs.

Resolve once, acquire once and build from that manifest. No build stage re-queries `latest` or clones an unrecorded HEAD. Exact source identity does not imply bit reproducibility unless every package repository and tool input is also fixed.

Keep Ubuntu 26.04 because the selected stack compiles on it. Use its normal signed repositories with weekly package-cache invalidation, not timestamped snapshots or a CA bundle borrowed from the Rust image. Record installed packages and retain tested image digests. Changing distro would add another compatibility investigation without removing the source components Wolf requires.

## Minimal runtime contents

Application-image scope is explicitly included after operator correction. Use independently authored common/Steam/Lutris stages, not copies of upstream Dockerfiles or inherited multi-vendor/EOL base-app images. Share package-managed Sway/Xwayland and amd64/i386 Intel graphics/audio-client libraries. Add only Steam's distribution installer or verified latest stable Lutris plus Wine dependencies to each target. Do not include a Pulse server, system networking/Bluetooth daemons, Decky, a custom gamepad UI, panels or terminal applications. Preserve Wolf's socket, identity, input, home and shared Lutris-library contract. Retain game compatibility and controller acceptance as separate unfinished checks. [Application image documentation](../../../compose/apps.md) owns commands and consumer details.

Application builds discover base and Lutris updates daily and refresh distribution packages daily. Embed release checksums, base/recipe identity and installed package versions. Upload size, SBOM and vulnerability reports. Candidate publication is independent from promotion and rollout. The existing protected promotion workflow selects the image and requires evidence bound to both repository name and digest. User-owned Steam client/Proton updates remain runtime-managed and are not falsely recorded as immutable distribution inputs.

Build and strip binaries/plugins separately from the runtime. Exclude compilers, headers, source trees and test assets. Remove NVIDIA NVRTC/CUDA paths, AMD-specific drivers and legacy i965/MediaSDK after proving no required plugin links or runtime loads depend on them. Do not build compositor CUDA features in the Intel-only target.

Initially preserve software H.264/HEVC/AV1 fallback elements used by supported upstream configuration. Remove an encoder or codec only when the project explicitly limits that behavior and its scenario passes without it. Keep the hardware encoding routes and their parsers, postprocessing, audio and transport elements.

GStreamer plugins and graphics drivers are dynamically discovered. Inventory plugin factories, inspect their load errors and exercise pipelines. `ldd` alone is insufficient. Mesa/LLVM libraries must be traced to retained rendering paths rather than removed by vendor-name heuristics. Desktop utilities, icon themes, fonts and broad format libraries are candidates, not automatically safe deletions.

Compare image layer size, unpacked footprint, plugin/library inventories and cold-start time using the same measurement method. Do not set an arbitrary size target that encourages broken runtime trimming. Smaller storage footprint is not a promise of higher game FPS.

## Shared gate and consuming configuration

The shared gate gains `GATE_PROFILE=persistent-proxy|port-handoff`. Absence preserves existing inference defaults. The handoff profile requires explicit generic `GATE_RUNTIME`, `GATE_CONTAINER_NAME`, `GATE_TCP_PORTS`, `GATE_UDP_PORTS` and `GATE_ACTIVITY_PREFIXES`. It uses `GATE_HOST`, `DOCKER_SOCKET`, `IDLE_TIMEOUT`, `STARTUP_TIMEOUT` and `CONNECTION_IDLE_TIMEOUT`. No Wolf-specific runtime name, ports or prefixes are hardcoded in gate.

The Wolf Compose YAML selects `port-handoff`, host `0.0.0.0`, runtime `wolf-runtime`, gate container name `wolf`, TCP `47984,47989,48010`, UDP `47999,48100,48200`, activity prefixes `wolf-,wolf_,wolf`, idle timeout `300`, startup timeout `90` and connection idle timeout `600`. These are protocol/example defaults, not a particular host's configuration. Pin the accepted gate image and Docker socket directly in YAML. Keep only the candidate image and host-specific device/group settings in `.env`. The handoff gate must exclude itself and the runtime from activity matching.

The inference example retains existing llama/Whisper environment variables and behavior. No generic backend-description language or embedded JSON environment blob is introduced merely for possible future consumers.

Remove the gate executable’s external JSON configuration path, `--config` flag and implicit file fallback in the shared-owner implementation. Internal typed configuration and validation may remain. Runtime state/configuration owned by Wolf, including its TOML and pairing certificates, is not gate configuration and is preserved.

## Deployment boundary

The example has a device-free, non-root, read-only gate on host networking and a separately created, stopped runtime under the `runtime` profile with `restart: "no"`. The runtime owns configured DRM devices, required input devices/udev, state and Docker socket access. Parameterize device paths and owning groups. Keep standard paths directly in YAML rather than adding variables for one-off edits. Do not blindly copy a whole `/dev` mount or grant extra privileges without checking upstream's concrete application/input requirements.

Gate releases all handoff listeners before runtime start, preserves the first TCP byte stream and drops the triggering UDP datagram for client retry. Readiness uses Docker health plus the configured TCP listeners, not an inference HTTP endpoint. Idle stop is suppressed while application containers are active, and Docker activity-inspection failure must not cause unsafe shutdown. Timeout cleanup and listener reacquisition remain required.

The initial runtime may retain a writable root filesystem if startup actually needs it. A read-only deployment is accepted only after enumerating writable state, sockets and temporary paths and testing the full session. Gate `--health` proves binary execution, not Docker permissions or streaming readiness.

## Update and promotion pipeline

Run daily in UTC and on relevant source changes, pull requests and manual requests. Discover all input owners, build when resolved inputs change and force a weekly base/package refresh to catch security updates not represented in application release tags. Allow a manual exact-version candidate. API failures, rate limits or unverifiable input must fail discovery rather than fall back to a moving source.

Run resolver/manifest tests, documentation/schema checks, workflow/Compose validation, license/SBOM checks, vulnerability assessment and final-image smoke checks before producing a candidate. Vulnerability exceptions require an explicit recorded rationale rather than suppressing the scanner. Build once and promote that same digest, without rebuilding between acceptance and publication.

PRs may test on disposable hosted runners but never publish or run untrusted code with a host Docker socket or on the trusted GPU runner. Serialize promotions per image. A failed update leaves the current `latest` unchanged and produces an actionable workflow failure with the candidate inputs and failing check.

Use a build-unique immutable tag such as `<wolf-version>-<input-hash>` because a dependency-only rebuild can share the same Wolf version. Validate tag syntax and detect identity collisions. Attach full source/input identity as OCI metadata and provenance. Operator-approved candidates may acquire testing `latest` after payload and vulnerability checks, without claiming full game/session acceptance. Optional complete evidence establishes that separate boundary. Keep historical versioned images available subject to an explicit retention policy.

## Acceptance and recovery

CI without an Intel GPU can establish binary startup, plugin availability, dynamic-link closure and configuration correctness. It cannot establish hardware encoding, zero-copy correctness or Moonlight session fidelity. Test the exact candidate digest on the intended Intel device, with a known working baseline and consistent settings.

Require H.264, HEVC and AV1 where the target advertises support, cold TCP/UDP start, pairing/reconnection, audio, keyboard/mouse/controller events, Steam/Lutris launch, sustained streaming, game-process exit, idle stop and DRM release. Compare frame/encoding latency, dropped frames, quality, CPU/GPU use and cold-start latency with recorded baseline tolerances. Do not hide software fallback as successful hardware encoding. Unsupported hardware features are explicitly marked not applicable with capability evidence.

Before authorized rollout, stop sessions and back up Wolf configuration, pairing state and application state consistently. Retain prior runtime and gate digests plus prior deployment settings. Test candidate state migration separately where upstream changes schemas. Image rollback alone does not undo state migrations. A gate restart's existing runtime-stop behavior must be documented so upgrade cannot unexpectedly interrupt a session.

## Implementation order

First deliver and test environment-only handoff in the shared gate, preserving inference. Next resolve exact inputs and build a conservative supported-base Wolf candidate. Then prune one dependency group at a time against plugin and session evidence. Finally enable the maintenance/promotion pipeline and deliver the consuming Compose template. Production rollout remains a separate authorized action.
