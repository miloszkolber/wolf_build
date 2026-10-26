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
