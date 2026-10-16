# Evidence and acceptance readiness

All three relabeled images are published and ready for operator game/session acceptance. Testing `latest` and host rollout are explicitly authorized separately from complete acceptance. Deployment backups, configuration and rollback records belong to the deployment owner, not this repository.

## Reviewed image set

Runtime workflow `38761490730` and application workflow `38761491024` passed on source `a1e4e9d`, including static checks, SBOMs, zero HIGH/CRITICAL findings and immutable publication. Full input identities match their downloaded CI artifacts. All three exact digests were pulled and rescanned successfully during the independent review.

| Published candidate | Exact digest |
| --- | --- |
| `ghcr.io/miloszkolber/wolf_runtime:stable-6a5053b4ebbb-f22620a7472d` | `sha256:6592b87e93d00f4702810f40b1a05063efcb04824fc37c57e3d2144c1ecb462d` |
| `ghcr.io/miloszkolber/wolf_steam:candidate-608f13424ac4e74b` | `sha256:cc58141eaf61ea8cdd1f53a5b36d35dda8316e469d99db064175493c826880ec` |
| `ghcr.io/miloszkolber/wolf_lutris:candidate-608f13424ac4e74b` | `sha256:cfcb07628f3034624d292450c3356911a256c1d6b4a8d42aa2663976f4f84cd1` |

Protected testing-latest promotions passed in runs `38830203743` (runtime), `38830206139` (Steam) and `38830208653` (Lutris), after explicit operator authorization and environment approval. All three `latest` manifests match the exact digests above. Payload and HIGH/CRITICAL gates were rerun by the promotion jobs. No full-acceptance evidence was fabricated.

The shared gate remains `816b5f152e99` at `sha256:791ef11cb13be5fbcc59ae5cdb77512c57a30bcb2ab5d729294cd09976e28b40`, owned and verified in `llama_build`.

## Executed checks

Runtime library/plugin/license checks and isolated Intel H.264, HEVC and AV1 encoding passed. Isolated gate/runtime checks passed health-without-wake, cold `/serverinfo`, readiness, idle stop and clean Wolf/Pulse exit. The authorized deployment also passed cold startup, normal idle shutdown with exit zero and listener reacquisition, and preserved pairing records. This is not proof of complete streaming quality or zero-copy behavior.

Both application images passed Intel library closure for amd64/i386, default/custom UID handling, rejected root-like IDs, real headless Sway/Xwayland fake-app sessions, two-run persistence, clean exit and injected fake-udev execution. The actual Lutris version command works with a disposable HOME. Stock bubblewrap user namespaces passed without SYS_ADMIN. A real Lutris frontend stayed running in an isolated probe, and Intel Vulkan device discovery passed. The offline Steam-state clone probe stopped at its expected network bootstrap; normal-network access to the verified installer URL passed. Actual Steam/game rendering, sound, controllers and complete streaming still require the operator's session tests.

Trimming excludes build/desktop/NVIDIA layers and separate non-Intel Vulkan drivers while retaining Intel's shared Gallium/LLVM and both graphics/audio ABIs. Gates exposed and repaired the unused vulnerable base `pebble` binary and a stale inherited OpenSSL provider. All reviewed images now scan clean without exceptions. Explicit pciutils/protobuf dependencies retain Lutris GPU detection and Battle.net support.

## Independent source corrections

The earlier identity-decoupling claim was incomplete: a content whitelist still recorded repository HEAD, so unrelated commits changed the identity. Runtime provenance now uses the last commit touching runtime-owned inputs. A temporary Git-history regression proves unrelated documentation/application commits preserve the complete identity. Build-context rules are included and unshipped promotion/probe scripts excluded.

Source checks pass with 29 Python tests, shell syntax, 17 Markdown files, strict OpenSpec and actionlint. The weekly maintenance prompt follows the sibling worker contract and was prepared without scheduling or executing a worker.

Protected promotion rechecks exact-image payload/vulnerability gates and stages `tested-<digest>` before changing `latest`. Operator-approved testing latest is not an accepted-session record. Optional complete evidence still requires matching repository/digest, real session checks and codec capability evidence. Scheduled builds publish candidates only.

## Open acceptance

Real Steam/Proton and Lutris native/Wine games, audio, controls/hotplug, latency/quality, zero-copy, reconnect, sustained sessions and idle DRM release remain operator acceptance items. The active change stays open until those results exist. No full acceptance or archive is claimed.
