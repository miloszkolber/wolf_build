# Evidence and verification status

Gate and Steam/Lutris candidates are published. Wolf images have built and passed bounded checks and local scans. Runtime registry publication and full game/session acceptance remain open. No production deployment or pairing state has changed. No accepted `latest` exists for any image.

## Published candidates

The application workflow passed on source `060dca2` (Actions run `38755980934`): both builds, bounded final-image/session checks, zero HIGH/CRITICAL findings, SBOM creation and separate publication jobs. Registry manifests were readable anonymously and their full input identities matched CI evidence. The published Steam digest was additionally pulled anonymously and its payload check passed. The large Lutris pull timed out during layer download, so Lutris verification used the registry manifest/config plus CI exact-image smoke evidence rather than a completed local pull.

| Public candidate | Published digest |
| --- | --- |
| `ghcr.io/miloszkolber/wolf_steam:candidate-54bdd4ad9b367169` | `sha256:d11afd56b77a55958839c52456cd2acffa88d5f518a9134c16e3b8e8731b2718` |
| `ghcr.io/miloszkolber/wolf_lutris:candidate-54bdd4ad9b367169` | `sha256:e784dc119ed40ea0bd7cd1b269b6fadec29776ffcee109dd2548913d214cd82d` |

These are unaccepted candidates, not `latest` promotions. Published gate `816b5f152e99` (`sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40`) passed both profile traffic tests and a read-only image health check. Gate internals belong to `llama_build` (`openspec/changes/archive/2026-10-15-universal-env-gate/`).

## Verified image checks

The runtime image builds from exact Git sources (Wolf `stable`, compatible GStreamer series, declared compositor/interpipe pins, Intel `26.3.5` media/VPL with declared libva/GMM/dispatcher, pinned Rust/base). Acquisition rejects object-identity mismatch, dirty caches and unrecorded refs. A network-isolated final-image run passed library/plugin/license checks. An isolated Intel probe passed H.264, HEVC and AV1 encode pipelines. The published gate drove a uniquely named test runtime through health-without-wake, cold `/serverinfo`, healthy startup and idle stop with clean Wolf/PulseAudio exit. These prove encoder availability and lifecycle behavior, not zero-copy capture, game quality or Moonlight acceptance.

Both application images passed payload/Intel library closure for both ABIs, default/custom identity, rejected root-like IDs, headless Sway/Xwayland fake-app sessions with two-run persistence and normal shutdown, the real Lutris version command as the application user and injected `fake-udev` execution. The recipe trims only separate non-Intel Vulkan drivers/ICDs inside the install layer and keeps shared Mesa/LLVM libraries. Lutris diagnostics added explicit `pciutils` (GPU detection) and `python3-protobuf` (Battle.net source) dependencies.

All three images generated SBOMs and passed HIGH/CRITICAL scans with zero findings. The gates correctly failed first: three HIGH Go advisories in the unused unowned `/usr/bin/pebble` (since removed and rejected by static checks), then one HIGH `CVE-2026-84782` in inherited `openssl-provider-legacy` (fixed by upgrading inherited base packages). No suppression or exception was added.

Source checks pass: 28 Python tests, application shell syntax, 17 Markdown files with zero failures, strict OpenSpec validation and actionlint. The lock fixture proves same-week discovery keeps identity stable while the next week changes it.

## Open acceptance

Runtime registry publication, full Moonlight sessions and accepted `latest` remain open. Session latency/quality, zero-copy behavior, real audio, controls, Steam/Lutris game integration and idle DRM release remain unverified. Hardware/deployment measurements belong outside this repository. The active change is not ready to archive.
