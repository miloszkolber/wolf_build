# GStreamer series security basis

## Why

At proposal time on 2026-10-26, the runtime built Wolf's declared GStreamer 1.26 series at `1.26.11`, released 2026-03-10. That was the last release in the series and no `1.26.12` existed. The GStreamer security centre named fixes for advisories published from 2026-04-07 through 2026-10-08 only in `1.28.2` through `1.28.8`, and those advisories affected GStreamer core, `gst-plugins-base`, `gst-plugins-good`, `gst-plugins-bad` and `gst-plugins-ugly`, all of which the image built. The `1.26` branch had backported some June fixes without a release and predated the July-October advisories.

The distribution vulnerability gate does not see these advisories because GStreamer is built from source rather than installed as distribution packages. The pre-change image therefore shipped known-unfixed parser and RTP code that no routine check reported. The delivered change selected `1.28.8`; the source-built stack still requires manual advisory review.

Wolf declared `1.26.7` at proposal time, so this was a graphics/media stack reselection rather than a routine patch refresh. It required build, plugin-closure and real-session evidence and operator authorization.

## What changes

- Replace the resolver's fixed series acceptance with a reviewed series selection that defaults to Wolf's declaration and records an explicit, justified divergence when a newer maintained series is adopted.
- Build the latest patch of the selected series (`1.28.8` today) and record its advisory basis in the manifest.
- Rebuild the compositor and interpipe against the selected series and extend the final-image check to prove the required factories still load.
- Enforce the manually reviewed advisory floor for an override. New advisories still need a separate review because the resolver does not discover them automatically.

## Capabilities

Modified capability is `intel-runtime`.

## Status and authority

Authorized and merged on 2026-10-26. Implementation and feature-level real-session acceptance are complete. Build evidence and the scope of session acceptance are tracked separately in the existing task ledger and evidence. Full digest and codec acceptance remain separate.

## Dependencies and consequential unknowns

- At proposal time, compatibility of Wolf, the compositor and interpipe with the new series was not established. The subsequent build and final-image checks are recorded in the evidence.
- The evidence records isolated VA and synthetic zero-copy checks, not QSV behavior or full codec and zero-copy acceptance in a real session. Those remain separate acceptance gaps.
- At proposal time, a future upstream move to 1.28 could have changed the need for the override. The configured override remains selected until explicitly changed or removed.
