# Evidence

## Reviewed series state, 2026-10-26

- Built identity: GStreamer `1.26.11`, tag commit `e6ee9e63e033b9c8e343ba0bdfa7590ef81449ee`, released 2026-03-10. No `1.26.12`, `1.26.13` or other later 1.26 tag exists.
- Wolf's declaration at the held source `6a5053b4ebbb19f2c0f3bf1e8fbbd8babf109273`: `ARG GSTREAMER_VERSION=1.26.7` in `docker/gstreamer.Dockerfile`. The beta head `9f29d9c` still declares `1.26.7`.
- Newest series releases: `1.28.8` (`1b2a95a1b72787cda146b46df9605b168e5b683b`, 2026-10-08) and a development `1.29.2`.
- `1.26` branch head: `765564f3ec`, 2026-06-29. It backports some June security fixes without a release and predates the July-October advisories.

## Advisories not covered by 1.26.11

From the [GStreamer security centre](https://gstreamer.freedesktop.org/security/), every advisory published from 2026-04-07 through 2026-10-08 names fixes in `1.28.2` through `1.28.8` only. Their affected components include:

| Component | Affected by advisories fixed in 1.28.2-1.28.8 |
| --- | --- |
| GStreamer core | SA-2026-0028, 0078, 0083 |
| gst-plugins-base | SA-2026-0014, 0019, 0023, 0030, 0032, 0033, 0034, 0053, 0054, 0082, 0083, 0088 |
| gst-plugins-good | SA-2026-0016, 0018, 0020, 0021, 0022, 0025, 0035, 0036, 0044, 0050, 0051, 0052, 0057, 0064, 0065, 0068, 0072, 0073, 0074, 0076, 0079, 0080, 0086, 0088, 0089, 0091 |
| gst-plugins-bad | SA-2026-0013, 0014, 0015, 0017, 0024, 0026, 0027, 0029, 0031, 0039, 0040, 0041, 0043, 0045, 0046, 0047, 0048, 0049, 0055, 0056, 0059, 0060, 0061, 0062, 0063, 0067, 0070, 0077, 0085, 0092 |
| gst-plugins-ugly | SA-2026-0042, 0058, 0066, 0071, 0075, 0087 |

`gst-libav`, `gst-rtsp-server` and `gst-editing-services` advisories are excluded because this image does not build those modules and Wolf implements its own RTSP server.

## Earlier fixes already in 1.26.11

The advisories published 2026-02-25 (SA-2026-0001 through 0012) were released before 1.26.11, and SA-2026-0008 states its 1.x range ends at 1.26.10. That indicates 1.26.11 carried the then-current fixes; it does not cover anything published afterwards.

## Coverage gap

The HIGH/CRITICAL Trivy gate assesses distribution packages. A source-built GStreamer is not mapped to distribution advisories, so these findings do not appear in CI vulnerability results. No second scanner was added for this review.

## Implementation checks

The resolver selected `1.28.8` at `1b2a95a1b72787cda146b46df9605b168e5b683b` during live upstream discovery, recorded Wolf's `1.26.7` declaration and the explicit override, and retained the current compositor and interpipe pins. The reviewed minimum `1.28.8` covers the advisory baseline listed above through 2026-10-08. An absent review date/reason, a review predating the advisory cutoff or a patch below the minimum fails resolution. New advisories still require normal source review rather than trusting the distribution-only scan.

Resolver regressions check the highest stable patch within the selected series, missing-tag failure, malformed review metadata, the minimum fixed version and divergence in the expanded manifest. Final-image checks now also require the loaded GStreamer version to match that manifest.

## Build and local verification, 2026-10-26

The first hosted build failed at GStreamer configure, before compiling: 1.28 plugin documentation resolves `plugins_cache_generator` before honouring `-Ddoc=disabled`, and `-Dauto_features=disabled` disabled the core subproject's `check` feature that defines it. The recipe now passes `-Dgstreamer:check=enabled`, the core submodule's option namespace. Tests, examples and documentation remain disabled. This adds the check library to the image as an accepted cost.

A local build of the same resolved inputs completed with GStreamer `1.28.8`. Configure reported `gst-plugins-bad:va`, `qsv`, `aom`, `x265`, `gst-plugins-ugly:x264`, `gst-plugins-good:pulse` and `gst-plugins-base:gl` enabled, and all five GStreamer subprojects finished. The final image reports `GStreamer 1.28.8`, the media driver is the stripped 41,473,712-byte build, and the static final-image check including the synthetic audio conversion chain passed. The runtime supervision checks passed for normal shutdown and killed embedded Pulse.

On the host's Arc Pro B50 the isolated Intel probe passed VA encoding for h264 (`vah264enc`), hevc (`vah265enc`) and av1 (`vaav1enc`). A disposable synthetic session with no Docker socket, network or production state selected `va` for all three codecs, used zero-copy on the render node, started the Wayland display and reached end of stream without pipeline parse errors. This is not Moonlight or game acceptance.

The local image measured 270,749,751 bytes uncompressed against 343,062,643 for the previously deployed runtime. The difference combines the stripped driver with the new series and check library; it is not a measured registry or transfer saving.

## Advisory status after the change

`1.28.8` carries the fixes named by the advisories published through 2026-10-08 for core, base, good, bad and ugly. No advisory published after that cutoff was reviewed for this change, and the distribution-only scan still does not cover the source-built stack. The next maintenance review must compare any newer advisory against `1.28.8` and move to a later 1.28 patch if one exists.
