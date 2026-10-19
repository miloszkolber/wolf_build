# Maintenance state

Reviewed cursor for the scheduled dependency review. It records what was actually inspected, not a promise that every upstream input was. Advance a source only through material reviewed, independently of implementation acceptance. Image identity still comes from the resolved input lock.

## Reviewed 2026-10-19

Local revision `4fa4477`. Published identities when this review started: `wolf_runtime` `latest` = `stable-6a5053b4ebbb-c65dea6f3ffc` = `sha256:bb66aef617c22504bbae03783eebe52341529e892e1aae289854c046a10117f3`, `wolf_steam` `latest` = `d3947a27cadc6391` = `sha256:40ed57667aadf983e7b536a804cd9446af7cb73d3da6b599f02356c58dcf86bd`, `wolf_heroic` `latest` = `b210d0a301287502` = `sha256:65e98f7cc9a41014d1676724729bd11eed2e0981fbc4eda917509d1c53b64f24`. Immutable and `latest` digests were equal for all three.

| Source | Reviewed identity | Inspected | Disposition |
| --- | --- | --- | --- |
| Wolf (`games-on-whales/wolf`) | Held at `6a5053b4ebbb19f2c0f3bf1e8fbbd8babf109273`; upstream `stable` is now `40b0c5cec44a7888a31d69db888ae2d3175ef36c`, `beta` `71a8242ef4c23363cbdf82a80efe74bfc364b8ce` | `docker/wolf.Dockerfile`, `docker/gstreamer.Dockerfile`, `.github/workflows/docker-build.yml`, `.github/workflows/release-channels.yml`, `.github/RELEASE_CHANNELS.md`, `docs/modules/user/pages/quickstart.adoc`, release list and tag list | Release channels migrated to `stable` = latest published GitHub release. The only published release is `v2024.07` (2024-07-10), which declares GStreamer 1.22.7 and no Rust toolchain argument, so the lock cannot read its build metadata. Discovery held at the last reviewed commit; `stable` tracking resumes at upstream's first calendar release. |
| Wolf base image move | `beta` `71a8242e` | `docker/wolf.Dockerfile`, `docker/gstreamer.Dockerfile`, Fedora commits `ea4ee16`, `18bc44b`, `9354b9a` | Fedora is now upstream's default base and its image chain is Fedora-only. This repository authors its own Ubuntu 26.04 recipes and does not copy upstream images. No receipt change. Ubuntu 26.04 is still a supported release with current updates. |
| GStreamer | `1.26.11` (`e6ee9e63e033b9c8e343ba0bdfa7590ef81449ee`) | Tag list for the `1.26` line | Latest patch in Wolf's declared compatible series. `1.28.x` and `1.29.x` exist upstream; Wolf still declares `1.26.7`, so no series change is adopted. No security-only release after `1.26.11`. |
| Compositor (`games-on-whales/gst-wayland-display`) | `016b4fc66d62b6a34c37169ecf6d511eef140d7c` (unchanged) | Wolf's declared pin, upstream branch and tag list | No change. |
| Interpipe (`games-on-whales/gst-interpipe`) | `0c454917cb3cf4f2b2f2729f5f72a4dee072c7c9` (unchanged) | `master` | No change. |
| Intel media stack | `intel-media-26.3.5`, `intel-onevpl-26.3.5`, `gmmlib 22.10.2`, `libva 2.24.1`, dispatcher `v2.17.0` (all unchanged) | Latest release metadata for `intel/media-driver`, `intel/vpl-gpu-rt`, `intel/libvpl` and the VPL release dependency table | Declared libva/GMM/dispatcher constraints still match the resolver's derived lock. No action. |
| Distribution base | `ubuntu:26.04` at `sha256:42527649dbc4f9197a6073f426f488cbff0e9cc9f2afce32d91c383e4875634a` | Docker Hub tag metadata for the amd64 digest | Base patch already resolved by the 2026-10-17 build and reused on 2026-10-18. Digest unchanged since; discovery adopts it automatically. |
| Rust toolchain | `rust:1.96.0-slim-bookworm` at `sha256:bef0c0c8eee5b866fadb56bd83cdf4681921c3851f2b01dc13b621653a06a4f5` (unchanged) | Wolf's declared `RUST_VERSION`, Docker Hub tag metadata | No action. |
| Distribution packages | Locked closure of the published runtime and both applications | `docker/packages/*.txt` against the resolved locks; CI resolution results | No retired or renamed selection reported by CI. Refreshes only through an actually changed resolution. |
| CMake dependencies | Wolf's declared `FetchContent` revisions | `lock_sources` declaration scan of the held source | Unchanged with the held source. |
| Applications | Heroic `v2.22.4` (unchanged), Steam via Ubuntu `steam-installer` | Heroic release metadata, `docker/apps.Dockerfile`, `docker/apps/*` | No action. Steam, Proton and Heroic-managed runners remain persistent user state. No Wine/winetricks package exists here. |
| Shared gate (`miloszkolber/gate`, owner `llama_build`) | Published `latest` = `d2f678bec2f5` = `sha256:cb14c151aabacd0e979951a94abcd9c05af67e79bbbe0e1b16deb7d9a5f0d401` | llama_build source `d2f678b` (`cmd/gate`, `cmd/gate/README.md`), gate workflow, gate registry tags | The example pinned `816b5f152e99` = `sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40`, which the registry no longer serves (404 by tag and by digest). The example now pins the published digest. Nothing under `cmd/gate`, `docker/gate.Dockerfile`, `go.mod` or the gate build inputs changed since the previous pin, and `/app/gate` is byte-identical (`5b82f890e67db233a1cdf86987c588f31efb77963835b6d26f7d909d1fb54a72`) between the two available publications, so the consumed gate implementation is unchanged. |
| Actions | Pinned SHAs in `.github/workflows/` | `.github/dependabot.yml`, workflow pins, latest releases of the used actions | `docker/setup-buildx-action` v4.4.1, `docker/login-action` v4.6.0 and `docker/build-push-action` v7.4.0 exist beyond the pinned versions. Dependabot owns github-actions bumps; no competing manual change was made. |

## Findings and repairs

- The runtime workflow resolved Wolf through branch `stable`. After the upstream migration, the same discovery returned the `v2024.07` snapshot and `resolve.py --lock` failed with `Wolf build metadata changed; review compatibility before building`, which would also stop base and package security refresh. `scripts/resolve.py` now holds the last reviewed commit and `tests/test_resolve.py` covers the hold and its clearing.
- The deployment example pinned a gate digest the registry no longer serves. It now pins the current published digest after the same-gate-implementation check above.
- No rebuild is required by this review on its own; the resolver change is a shipped recipe change, so the next default-channel run grows a new runtime identity even though Wolf, GStreamer, Intel and base inputs are unchanged.

## Failed or inaccessible

- `games-on-whales/wolf` releases API returns only `v2024.07`, `v2023.06`, `v2023.02` and `v2022.11`; no calendar release tag exists, so upstream's new `stable` rule cannot yet select a 2026 source.
- The previously pinned gate digest `sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40` is no longer retrievable, so that rollback reference is unavailable.
- GStreamer's advisories page did not render usable content for automated reading; coverage for that source is the release/tag list, which shows no release after `1.26.11`.

## Not covered by this review

- No Intel device probe, GPU encode, Moonlight session, audio or controller acceptance was run. Full-session acceptance remains a separate operator record.
- Distribution package closures are resolved by CI; this review did not re-resolve them locally.
- No host deployment, service restart or state migration was performed.
