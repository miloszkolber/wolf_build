# Maintenance state

Reviewed cursor for the scheduled dependency review. It records what was actually inspected, not a promise that every upstream input was. Advance a source only through material reviewed, independently of implementation acceptance. Image identity still comes from the resolved input lock.

## Reviewed 2026-10-26

Local revision at review start: `080aa1b`. Reviewed recipe and configuration paths: `docker/wolf.Dockerfile`, `docker/apps.Dockerfile`, `docker/packages/*.txt`, `docker/runtime/wolf-session-idle.conf`, `scripts/resolve.py`, `scripts/resolve-apps.py`, `scripts/build-inputs.py`, `scripts/lock-packages.py`, `compose/docker-compose.yaml`, `compose/.env.example`, `.github/workflows/build.yml`, `.github/workflows/apps.yml`, `.github/workflows/docs.yml`, `.github/dependabot.yml`.

Published identities when this review started, all with immutable tag and `latest` on the same digest: `wolf_runtime` `stable-6a5053b4ebbb-33bf3cfe73a6` = `sha256:cc6ce1f93d1b3aa90252536546ddb2deb93d87558566e652403516466c2b9e19`, `wolf_steam` `f9f265759c315f41` = `sha256:c270e8e308541f455a74c6813c33bb653ac531ea70c0b98df72341b2a7952f47`, `wolf_heroic` `6c181db66066f66f` = `sha256:2ad590f25f04dae0c379f0946b314e453138674ccb60bfe9d9838217201f7da0`.

| Source | Reviewed identity | Inspected | Disposition |
| --- | --- | --- | --- |
| Wolf (`games-on-whales/wolf`) | Held at `6a5053b4ebbb19f2c0f3bf1e8fbbd8babf109273`; upstream `stable` remains `40b0c5cec44a7888a31d69db888ae2d3175ef36c` (`v2024.07`, 2024-07-10); `beta` is now `9f29d9c4ceb5b0fb83875d98dad67af8237f5495` | `docker/wolf.Dockerfile` and `docker/gstreamer.Dockerfile` at the beta head, every commit from the previously reviewed `71a8242` to `9f29d9c`, release list, tag list and GitHub advisories | No calendar release exists, so the hold stays. The only source change is `7703d10`, a 7.1 Opus channel-map fix that arrives with a future source adoption; it is not cherry-picked into the held build. `94bc47a`/`c661e7a` are Fedora RPM Fusion packages and do not apply to the independently authored Ubuntu recipe. |
| GStreamer | `1.26.11` (`e6ee9e63e033b9c8e343ba0bdfa7590ef81449ee`, 2026-03-10), the last release in that series | Tag lists for the 1.26, 1.28 and 1.29 lines, the `1.26` branch and its commits, and the [security advisories](https://gstreamer.freedesktop.org/security/) with their affected versions | No later 1.26 release and no 1.26.12 tag. Advisories published from 2026-04-07 through 2026-10-08 name fixes in 1.28.2-1.28.8 only, and several affect core, base, good, bad and ugly components that this image builds. The `1.26` branch head (`765564f`, 2026-06-29) backports some June fixes without a release and predates the July-October advisories. This is a media-stack series decision, now recorded in the active [GStreamer 1.28 change](changes/gstreamer-1.28-series/proposal.md) with operator authorization. |
| Compositor (`games-on-whales/gst-wayland-display`) | `016b4fc66d62b6a34c37169ecf6d511eef140d7c` | Wolf's declared pin and the upstream `master` head, which is the same commit | No change. |
| Interpipe (`games-on-whales/gst-interpipe`) | `0c454917cb3cf4f2b2f2729f5f72a4dee072c7c9` | `master` | No change. |
| Intel media stack | `intel-media-26.3.5`, `intel-onevpl-26.3.5`, `gmmlib 22.10.2`, `libva 2.24.1`, dispatcher `v2.17.0` | Latest release metadata for `intel/media-driver`, `intel/vpl-gpu-rt`, `intel/libvpl`, `intel/libva` and the VPL 26.3.5 release dependency table | All unchanged and still matching the resolver's derived lock. No advisories published for these repositories. |
| Distribution base | `ubuntu:26.04` at `sha256:42527649dbc4f9197a6073f426f488cbff0e9cc9f2afce32d91c383e4875634a` (Docker Hub update 2026-10-17) | Docker Hub amd64 digest | Unchanged since the previous review; discovery adopts it automatically. |
| Rust toolchain | `rust:1.96.0-slim-bookworm` at `sha256:bef0c0c8eee5b866fadb56bd83cdf4681921c3851f2b01dc13b621653a06a4f5` | Wolf's declared `RUST_VERSION` and Docker Hub amd64 digest | Unchanged. |
| Distribution packages | Locked build and runtime closures | Resolver and package-lock code paths, and the 2026-10-24/25 CI resolution results: the 2026-10-25 runtime run reused its published image, and the 2026-10-24 application rebuild was attributed to the recipe hash only | No local action. CI resolves package versions; this review did not re-resolve them. |
| CMake dependencies | Wolf's declared `FetchContent` revisions | Declaration scan of the held source | Unchanged with the held source. |
| Applications | Heroic `v2.22.4`; Steam via Ubuntu `steam-installer` | Heroic release metadata, `docker/apps.Dockerfile`, `docker/apps/*` | No change. Steam, Proton and Heroic-managed runners remain persistent user state. |
| Shared gate (`miloszkolber/gate`, owner `llama_build`) | Pinned `d2f678bec2f5` = `sha256:cb14c151aabacd0e979951a94abcd9c05af67e79bbbe0e1b16deb7d9a5f0d401`, still served; adopted `e5d62a041306` = `sha256:803d36eda9789db2ba88f0420222d76e71d232e89f55ab92b5f742981c4dbfcc` (2026-10-24); publisher later moved `latest` to `0c7b0cb881ed` = `sha256:c7fa85663b631c664e4365ab37f1154dcb7e2207e050c21d92e8048372f3a3e3` | llama_build `cmd/gate` history and `cmd/gate/README.md` at `e5d62a0`, the gate change and its evidence, registry tags and image labels, and the `/app/gate` binary of both publications | Adopted the published digest and enabled the plaintext discovery cache for `/serverinfo` on the handoff control port. The environment contract is unchanged; the new settings are optional, and the only binary change since the previous pin is the discovery cache (`be8d2c8`, `e5d62a0`). The later `0c7b0cb881ed` publication is a rebuild with a byte-identical `/app/gate` (`sha256:503c2c61…`), so the example keeps the earlier verified pin, which the registry still serves. |
| Actions | Pinned SHAs in `.github/workflows/` | `.github/dependabot.yml`, workflow pins, latest releases of the used actions | `docker/setup-buildx-action` v4.4.1, `docker/login-action` v4.7.0 and `docker/build-push-action` v7.4.0 exist beyond the pinned versions. Dependabot owns `github-actions` bumps and has no open PR; no competing manual change was made. |

## Findings and repairs

- GStreamer 1.26.11 carries known advisories. The security centre's advisories published from 2026-04-07 through 2026-10-08 name fixes in 1.28.2-1.28.8 only, and they affect GStreamer core, `gst-plugins-base`, `gst-plugins-good`, `gst-plugins-bad` and `gst-plugins-ugly`, all of which this image builds. There is no 1.26 release after 1.26.11, and the `1.26` branch head (`765564f`, 2026-06-29) only backports some June fixes. `gst-libav`, `gst-rtsp-server` and `gst-editing-services` advisories do not apply because those modules are not built, and Wolf implements its own RTSP server. Moving to 1.28.x is a graphics/media stack reselection, so the scoped [GStreamer 1.28 change](changes/gstreamer-1.28-series/proposal.md) is active with operator authorization; its build, plugin-closure and session tasks remain open.
- Source-built components are outside the distribution advisory feed, so the Trivy HIGH/CRITICAL gate does not see these GStreamer advisories. This is a known coverage limit of the current gate, recorded here rather than worked around with a second scanner.
- The deployment example pinned an older gate publication than the one the gate owner verified and deployed. It now pins `e5d62a0` and sets `GATE_DISCOVERY_PORT`/`GATE_DISCOVERY_PATHS`, so a client that keeps polling plaintext discovery no longer cycles the runtime. The cache lives in the gate process; the first probe after a gate restart and any different host or path still start the runtime, and encrypted discovery is unchanged.
- `compose/README.md` still described Steam/Lutris images; Lutris was retired in favour of Heroic. Both references now name the current targets.
- The 2026-10-25 scheduled runtime run resolved the unchanged input identity, reused the published image, repeated its checks and republished `latest` at the same digest. The 2026-10-24 application run rebuilt both images because the Heroic sandbox recipe changed; upstream application inputs were unchanged.
- The gate publisher moved `latest` to `0c7b0cb881ed` after this review's cursor was recorded. Its `/app/gate` is byte-identical to the adopted `e5d62a041306` (`sha256:503c2c61…`), so this is a rebuild identity rather than a new implementation. On operator instruction the consuming deployment was then refreshed to that publication during an idle window: the runtime image was already current and stayed stopped, a cold `GET /serverinfo` started it and returned Wolf's server info, gate stopped it after the 300 s idle timeout, and the identical response was then served from the cache while the runtime stayed stopped.

## Previous reviewed identity

The 2026-10-19 review held Wolf at the same source commit and recorded GStreamer `1.26.11`, compositor `016b4fc`, interpipe `0c45491`, the same Intel stack, `ubuntu:26.04` at the same digest and `rust:1.96.0-slim-bookworm` at the same digest. Its repairs were the Wolf source hold, the gate pin alignment and repository metadata-only identity fixes.

## Rollback references

- Current checked runtime digest: `sha256:cc6ce1f93d1b3aa90252536546ddb2deb93d87558566e652403516466c2b9e19`.
- Previous accepted runtime digest: `sha256:0ee580beef1791d3430ee7e838fce3dbf2543a480ab66be1433377ebe5e7bcc6`.
- Current checked application digests: `sha256:c270e8e308541f455a74c6813c33bb653ac531ea70c0b98df72341b2a7952f47` (Steam) and `sha256:2ad590f25f04dae0c379f0946b314e453138674ccb60bfe9d9838217201f7da0` (Heroic).
- Previous accepted application digests: `sha256:f740f07ccab89f1b8e35c5346bcf822c02b65ec33d59bbd9683817c173d24d49` (Steam) and `sha256:bf936df731939e4bebd965a5f72fad0fcb71a7a6ac1379485a98320eaef15e32` (Heroic).
- Gate rollback pin: `d2f678bec2f5` = `sha256:cb14c151aabacd0e979951a94abcd9c05af67e79bbbe0e1b16deb7d9a5f0d401`, registry availability rechecked this run.

## Executed checks

- 68 unit tests, `check-docs.mjs` (30 Markdown files), strict OpenSpec validation, actionlint 1.7.12 and Compose configuration validation pass in the development container.
- The adopted gate digest was pulled and executed with `--health` (exit 0), and a bounded startup probe with the example's port-handoff and discovery settings in an isolated network namespace accepted the settings and then failed only on the absent Docker socket, as designed. The discovery-cache behaviour itself was verified by the gate owner, not repeated here.
- Pushed revision `a74461a`. Documentation run `40272998320` passed. Runtime run `40272998340` reused the unchanged immutable image, repeated its checks and republished `latest` at the same digest; its first two attempts failed only because the Trivy vulnerability DB download from `mirror.gcr.io` returned a 404 for one layer, and the retry passed the SBOM and HIGH/CRITICAL gates. `latest` and `stable-6a5053b4ebbb-33bf3cfe73a6` both resolve to `sha256:cc6ce1f93d1b3aa90252536546ddb2deb93d87558566e652403516466c2b9e19` afterwards.
- Earlier CI evidence for the same identities: runtime run `40174674780` (2026-10-25 scheduled reuse) and application run `40128732987` (2026-10-24 rebuild and publication). The 2026-10-26 scheduled runs on revision `1afd8f7` also passed: runtime `40291292639` reused the unchanged image and republished `latest`, and application `40297647351` reused and republished both unchanged application digests.

## Failed or inaccessible

- The Trivy vulnerability DB download failed twice on 2026-10-26 with a 404 from the `mirror.gcr.io` artifact cache, then succeeded on retry and in a standalone `--download-db-only` run. This was an external mirror failure, not a finding in the image.
- No source was unreachable. GitHub security advisories for Wolf, the compositor, interpipe, Heroic and the Intel components are empty, which is coverage by absence of publications, not a security audit.
- The weekly application schedule had not started when this review finished, so its 2026-10-26 result was not observed.

## Not covered by this review

- No GStreamer 1.28 build was attempted and no Wolf source newer than the hold was built.
- No Intel device probe, GPU encode, Moonlight session, audio, controller or idle-stop acceptance was run. Full-session acceptance remains a separate operator record.
- Distribution package closures were resolved by CI, not re-resolved locally, and base-image contents were compared by digest, not unpacked.
- No host deployment, service restart or state migration was performed by the review itself; the later operator-authorized gate refresh and its host verification are recorded in the findings above.
