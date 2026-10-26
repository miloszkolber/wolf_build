# GStreamer series security basis

## Why

The runtime builds Wolf's declared GStreamer 1.26 series at `1.26.11`, released 2026-03-10. That is the last release in the series and no `1.26.12` exists. The GStreamer security centre names fixes for advisories published from 2026-04-07 through 2026-10-08 only in `1.28.2` through `1.28.8`, and those advisories affect GStreamer core, `gst-plugins-base`, `gst-plugins-good`, `gst-plugins-bad` and `gst-plugins-ugly`, all of which this image builds. The `1.26` branch backports some June fixes without a release and predates the July-October advisories.

The distribution vulnerability gate does not see these advisories because GStreamer is built from source rather than installed as distribution packages. The current image therefore ships known-unfixed parser and RTP code that no routine check reports.

Wolf still declares `1.26.7`, so this is a graphics/media stack reselection rather than a routine patch refresh. It needs build, plugin-closure and real-session evidence and operator authorization.

## What changes

- Replace the resolver's fixed series acceptance with a reviewed series selection that defaults to Wolf's declaration and records an explicit, justified divergence when a newer maintained series is adopted.
- Build the latest patch of the selected series (`1.28.8` today) and record its advisory basis in the manifest.
- Rebuild the compositor and interpipe against the selected series and extend the final-image check to prove the required factories still load.
- Add a check that fails when the selected series has no security release covering the newest reviewed advisory, instead of silently building an unmaintained series.

## Capabilities

Modified capability is `intel-runtime`.

## Status and authority

Authorized and merged on 2026-10-26. Implementation is in progress with the repository reliability repairs. Build evidence and session acceptance are tracked separately in the existing task ledger. The change stays active until it is delivered and verified, then archives into the implemented contract.

## Dependencies and consequential unknowns

- Wolf, the compositor and interpipe must build against the new series; GStreamer 1.x API compatibility is expected but not established for this pin.
- VA and QSV plugin behaviour, zero-copy negotiation and CUDA-free plugin selection must be rechecked on the accepted Intel target, not just by factory presence.
- Upstream Wolf may move to 1.28 on its own; that would make part of this change unnecessary, so it is worth rechecking the Wolf declaration before starting.
