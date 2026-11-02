# Maintenance state

Reviewed cursor for the scheduled dependency review. It records what was actually inspected, not a promise that every upstream input was. Advance a source only through material reviewed, independently of implementation acceptance. Image identity still comes from the resolved input lock.

## Reviewed 2026-11-02

Local revision at review start: `912e8dd`. This review merged `6a99947` (Wolf release tracking) and `7894e7a` (action version comments) on top of `8b2a93e` (Dependabot merge) and published the identities below.

Reviewed recipe and configuration paths: `docker/wolf.Dockerfile`, `docker/apps.Dockerfile`, `docker/packages/*.txt`, `docker/runtime/wolf-session-idle.conf`, `scripts/resolve.py`, `scripts/resolve-apps.py`, `scripts/build-inputs.py`, `scripts/lock-packages.py`, `compose/docker-compose.yaml`, `compose/.env.example`, `.github/workflows/build.yml`, `.github/workflows/app.yml`, `.github/workflows/apps.yml`, `.github/workflows/docs.yml`, `.github/dependabot.yml`.

Published identities when this review started: `wolf_runtime` `stable-6a5053b4ebbb-4f182cf2d3da` = `sha256:8d61f36e3e4b6e49a637b41fe6b46346520a37bb576c836ccbc74a011d79889c`, `wolf_steam` `78b399b2b778387f` = `sha256:ea70280fbb6917826a2ae28b100596b5a457126859c06416c46d7d15863390b9`, `wolf_heroic` `c820849602e70256` = `sha256:b14422be1a3ccdcb96f404119e1405ce5fa40f6955a29f9543b82b2e1bbea1f3`. The runtime and applications were on different publication dates because the application schedule is weekly.

| Source | Reviewed identity | Inspected | Disposition |
| --- | --- | --- | --- |
| Wolf (`games-on-whales/wolf`) | `v2026.11` = `db709cfd3f0f49dfd7d00495940119309692b535` (2026-11-01); upstream `stable` now points at it, `beta` is `adf78d6061b872673c7d513bca6b683daec55466` | Every commit from the previously reviewed `9f29d9c` to `db709cf`, `docker/wolf.Dockerfile`, `docker/gstreamer.Dockerfile`, `docker/startup.sh`, `docker/supervisord.conf`, `src/moonlight-server` diff, default config templates, release notes, release/tag lists and GitHub advisories | This is the first calendar release the old hold waited for. It declares the same GStreamer `1.26.7`, Rust `1.96.0` and compositor `016b4fc`; startup, supervisor and the `/api/v1/events` and session endpoints are unchanged. The source delta is DRM descriptor ownership, the configured mDNS port and the 7.1 Opus channel mapping, plus the already-reviewed Fedora image chain. The hold is cleared and discovery tracks the release channel again. |
| GStreamer | `1.28.8` (`1b2a95a1b72787cda146b46df9605b168e5b683b`, 2026-10-08) | Tag list and the [security centre](https://gstreamer.freedesktop.org/security/) through 2026-11-02 | Still the newest 1.28 tag and the newest published advisory is SA-2026-0092 on 2026-10-08. No newer advisory or patch exists, so the reviewed floor and advisory cutoff are unchanged. |
| Compositor (`games-on-whales/gst-wayland-display`) | `016b4fc66d62b6a34c37169ecf6d511eef140d7c` | Repository default branch, branch list, commit list and Wolf's declared pin | The repository moved its default branch from `master` to `stable`; `stable` is exactly the pinned `016b4fc`, so the consumed commit is unchanged. |
| Interpipe (`games-on-whales/gst-interpipe`) | `0c454917cb3cf4f2b2f2729f5f72a4dee072c7c9` | `master` | No change. |
| Intel media stack | `intel-media-26.3.5`, `intel-onevpl-26.3.5`, `gmmlib 22.10.2`, `libva 2.24.1`, dispatcher `v2.17.0` | Latest release metadata for `intel/media-driver`, `intel/vpl-gpu-rt`, `intel/libvpl`, `intel/libva` and the VPL 26.3.5 dependency table | Unchanged. |
| Distribution base | `ubuntu:26.04` at `sha256:157dc3d6e4a3e4f2c68d12df9df9ed6e808b59af6d4c3757b432b4f519916725` | Docker Hub amd64 digest and the resolved manifest | Supersedes `42527649…`, which the 2026-10-26 review recorded. The first build on the new digest was the 2026-10-27 runtime run; today's application builds picked it up for the first time. |
| Rust toolchain | `rust:1.96.0-slim-bookworm` at `sha256:bef0c0c8eee5b866fadb56bd83cdf4681921c3851f2b01dc13b621653a06a4f5` | Wolf's declared `RUST_VERSION` and Docker Hub amd64 digest | Unchanged. |
| Distribution packages | Locked build and runtime closures | CI resolution results and build justifications | The 2026-10-28 runtime build took `linux-libc-dev` `7.0.0-38.38` to `7.0.0-42.42`; later scheduled runs reused the result. Today's builds resolved the current closure, which changed the application identities through the new base. No local action. |
| CMake dependencies | Wolf's declared `FetchContent` revisions | The resolved manifest compared with the previously published one | 21 of 22 acquired sources are unchanged; only Wolf moved. No new dependency or toolchain minimum. |
| Applications | Heroic `v2.22.4`; Steam via Ubuntu `steam-installer` | Heroic release metadata, `docker/apps.Dockerfile`, `docker/apps/*` | No upstream change. Both images rebuilt today after the base digest moved and the shared resolver recipe changed; Steam, Proton and Heroic-managed runners remain persistent user state. |
| Shared gate (`miloszkolber/gate`, owner `llama_build`) | Published `latest` = `0c7b0cb881ed` = `sha256:c7fa85663b631c664e4365ab37f1154dcb7e2207e050c21d92e8048372f3a3e3`; example pin `e5d62a041306` = `sha256:803d36eda9789db2ba88f0420222d76e71d232e89f55ab92b5f742981c4dbfcc` | Registry tags and the example pin | No new publication; both digests are served. The pin still names the verified publication with the discovery cache. |
| Actions | Pinned SHAs in `.github/workflows/` | `.github/dependabot.yml`, Dependabot PR #5, workflow pins, latest release tags | Merged PR #5 (`docker/login-action` v4.7.0, previously pinned SHA was v4.6.0) and corrected the stale version comments. `docker/setup-buildx-action` v4.4.1 and `docker/build-push-action` v7.4.0 remain ahead; Dependabot owns that channel. |

## Findings and repairs

- The Wolf source hold is cleared. `scripts/resolve.py` no longer pins `6a5053b`; `discover_wolf_stable()` reads `refs/heads/stable`, which now tracks the monthly release. `tests/test_resolve.py` checks the release-channel path, the explicit-hold path and the invalid-pin failure instead of asserting a permanent pin.
- The first build on the new source published `wolf_runtime` `stable-db709cfd3f0f-1eb37a02752a` = `sha256:6c65fbd531132daa22597f196f5bdee2639c1184c678dd5ea22a6700056e1c39` (run `41392210056`), with immutable tag and `latest` on the same digest. The build justification named packaging, sources and Wolf as the changed inputs.
- The push-triggered application runs rebuilt both images. The merge commit `8b2a93e` first built them on the new base digest (`d5e7afadaab6ed1b` and `c615d2f7a61f10a3`); the review's resolver change then built `wolf_steam` `e1a0301f081825cf` = `sha256:8590060c808388b5ce91bf070962e7b0db6caefb1d0ebd18a5e8a5606236de16` and `wolf_heroic` `af31fa3ebe9888fa` = `sha256:c2b4834f31c696d9575de3295c08bd8c18ede567981e41972e4fdbd784174228` (run `41392210091`), with immutable tag and `latest` equal. The intermediate identities stay published as immutable candidates. The weekly application schedule for this date had not run yet.
- The pinned `docker/login-action` SHA was v4.6.0 while the workflow comments claimed v4.1.0. PR #5 moved it to v4.7.0 and the comments now name that version.
- The GStreamer advisory floor was rechecked and did not move: `1.28.8` remains the newest tag and no advisory was published after 2026-10-08. The resolver's review metadata is part of the image identity, so it was left unchanged rather than rewritten as bookkeeping.
- The previous cursor still showed the 2026-10-26 identities and the retired base digest; this section replaces them.

## Previous reviewed identity

The 2026-10-26 review activated the GStreamer 1.28 change and adopted the gate discovery cache. Its cursor recorded Wolf `6a5053b`, GStreamer `1.26.11` (before the series change), compositor `016b4fc`, interpipe `0c45491`, the same Intel stack, `ubuntu:26.04` at `42527649…` and `rust:1.96.0-slim-bookworm` at `bef0c0c8…`. The follow-up GStreamer implementation landed in `a527a98` and published the series change before this review.

## Rollback references

- Current checked runtime digest: `sha256:6c65fbd531132daa22597f196f5bdee2639c1184c678dd5ea22a6700056e1c39`.
- Previous runtime digest: `sha256:8d61f36e3e4b6e49a637b41fe6b46346520a37bb576c836ccbc74a011d79889c`.
- Older accepted runtime digest: `sha256:0ee580beef1791d3430ee7e838fce3dbf2543a480ab66be1433377ebe5e7bcc6`.
- Current checked application digests: `sha256:8590060c808388b5ce91bf070962e7b0db6caefb1d0ebd18a5e8a5606236de16` (Steam) and `sha256:c2b4834f31c696d9575de3295c08bd8c18ede567981e41972e4fdbd784174228` (Heroic).
- Previous application digests: `sha256:ea70280fbb6917826a2ae28b100596b5a457126859c06416c46d7d15863390b9` (Steam) and `sha256:b14422be1a3ccdcb96f404119e1405ce5fa40f6955a29f9543b82b2e1bbea1f3` (Heroic).
- Gate rollback pin: `d2f678bec2f5` = `sha256:cb14c151aabacd0e979951a94abcd9c05af67e79bbbe0e1b16deb7d9a5f0d401`, registry availability rechecked this run.

## Executed checks

- 82 unit tests, `check-docs.mjs` (35 Markdown files), strict OpenSpec validation (6 items), actionlint 1.7.12 and Compose configuration validation pass in the development container.
- A local `resolve.py --lock` ran the full discovery path: Wolf `db709cf`, GStreamer `1.28.8` with the reviewed `1.26.7` divergence, unchanged compositor, interpipe and Intel pins, and the new base digest.
- The published runtime image was pulled and checked outside CI: Wolf revision label `db709cf`, GStreamer `1.28.8`, the static final-image check passed and Wolf started. The CUDA loader warning is expected because no NVIDIA payload is shipped.
- CI: runtime run `41392210056`, application run `41392210091` and documentation run `41392209965` passed on `7894e7a`. The earlier `8b2a93e` push reused the runtime and refreshed both application images; its runs `41392114607`, `41392114657` and `41392114586` also passed. Scheduled runtime runs from 2026-10-27 through 2026-11-01 passed and reused `8d61f36e`.

## Failed or inaccessible

- No source or advisory page was unreachable this run. GitHub security advisories for Wolf, the compositor, interpipe, Heroic and the Intel components remain empty, which is coverage by absence of publications, not a security audit.
- The 2026-11-02 scheduled runtime run had not executed when the review began; the push-triggered run supplied the changed-input build instead.

## Not covered by this review

- No Intel device probe, GPU encode, Moonlight session, audio, controller or idle-stop acceptance was run for the new digests. Publication is not acceptance.
- The [GStreamer 1.28 change](changes/archive/2026-11-02-gstreamer-1.28-series/proposal.md) records the user's 2026-11-02 real-TV feature-level session attestation separately from full digest and codec acceptance. The operator also accepted the [session idle and Gamescope change](changes/archive/2026-11-02-session-idle-and-gamescope/proposal.md) without providing exact test details or image identities for that earlier attestation.
- Distribution package closures were resolved by CI, not re-resolved locally, and base-image contents were compared by digest, not unpacked.
- No host deployment or service restart was performed by this review.
