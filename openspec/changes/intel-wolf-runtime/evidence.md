# Evidence and acceptance readiness

## GOG-first launcher replacement

Heroic replaces the Lutris target, resolver, publication matrix and maintained acceptance interface. Acquisition selects the stable amd64 deb and verifies its upstream SHA256. Heroic starts with `--console --fullscreen`, retains both graphics/audio ABIs and manages Proton/UMU in user state rather than shipping a second distribution Wine stack. The retired image name is rejected by the shared publisher. Historical evidence remains historical, not a build target.

Local Heroic and Steam builds passed headless/nested session probes with persistence and non-root identity. A real isolated Heroic 2.22.4 launch reported `Frontend Ready` and exposed a fullscreen Wayland window. Probing its bundled GOG/other store tools found a missing Python interpreter despite the deb installing successfully. Python is now explicit and final-image checks execute `gogdl`, `legendary` and `nile` version commands. The corrected local payload check passes all three helpers. These do not establish authenticated GOG downloads or game acceptance.

The misleading Steam network indicator has an evidenced consumer for a private system bus/NetworkManager. An isolated bridge-network probe without NET_ADMIN or NET_RAW reported `connected:full` after observing Docker's externally configured interface and a real HTTP connectivity check. The maintained config disables DNS management and automatic new connections. It does not expose the host bus or host network management. Session checks require the status service to be available to the non-root app. Nested Sway hides the cursor on typing and inactivity. TV-remote event delivery still requires client-specific verification.

CI `38956695959` passed both final images, store-helper execution, headless/nested session checks, SBOM and vulnerability gates. Published latest digests are Steam `sha256:a42d36400d77a6fc38ec738bde95b747d637a89002eec773c0cac55f48aa1296` and Heroic `sha256:ad522348a090cc7d86b4e9dfff6cacb6f52b14bf6f8a4bf200adfb341477160b`. The registry Heroic image again reported `Frontend Ready`, a fullscreen Wayland window and a working GOG helper in an isolated probe. The registry Steam image's real startup path exposed `connected:full` to its non-root app through the private status service.

The consuming profile now exposes Steam and Heroic, not Lutris, while preserving pairing and existing library data. Retirement workflow `38957844965` removed the old container package and Lutris image/evidence artifacts after replacement checks. Package metadata returned 404 and artifact enumeration found no remaining Lutris artifacts. Retired local images, temporary probe builds and obsolete acquisition files were removed. The one-time cleanup workflow was disabled and removed from source. Shared runtime/application build caches and unrelated CI history are not indiscriminately pruned.

## Live launch fixes

Actual Wolf launches revealed two omissions not covered by earlier isolated startup checks: the default audio chain requires `audiorate`, and non-root applications cannot connect to the compositor's root-owned Wayland socket. Both Steam and Lutris exited with `Could not connect to remote display: Permission denied`. The runtime now builds/checks audiorate and executes a synthetic version of the default conversion/Opus chain without sound devices. The app root setup transfers only the supplied Wayland socket to the configured non-root identity before dropping privileges, without recursive ownership changes or broadening permissions for all users.

The session check now includes a real nested compositor with an intentionally root-owned mode-600 parent socket. The previous image reproduces the same permission-denied exit at this boundary. Both patched Steam and Lutris images pass headless and nested session probes, Xwayland, custom UID/GID and persistence. CI `38948883691` also passed both final images and published latest: Steam `sha256:a44a8029b98b87b5e7620f5cdd638ce6bf856c78c11dc50a638ae8cf6677ba9d`, Lutris `sha256:9747ef2851ae594801e00e8d0a2214f0f56c60d77c02b4d104c9d475154c2bc7`. The automated check uses a fake application payload. Subsequent actual user launches passed compositor startup: Lutris initialized its frontend, while Steam ran its real client/update process. These establish launch-boundary repair, not rendered UI, game or audio acceptance.

Runtime audio-fix CI `38948381614` subsequently passed the complete build, static checks, synthetic audio conversion/Opus pipeline, SBOM and vulnerability gates and published `sha256:484a8e54bf1fcd926c760bb19604e72ec25678e8b93ff8522b348d1d75613d84` as latest. A fresh isolated final-image check also passed after pulling this digest. Live application remains separate from publication and must not interrupt an active session.

## Publication cleanup

Registry inspection confirmed that successful default-branch builds published newer immutable tags while latest remained on the manually promoted image. The separate promotion workflow was the only latest writer. Comparing runtime manifests from runs `38830204146` and `38868876511` showed identical runtime inputs/content hashes and refresh week, with only packaging revision changing from `d9a501a` to documentation commit `9258a85`. The cause was a shallow CI checkout hiding the real last input-changing commit.

Runtime and application publishers now share identity-checked immutable publication and automatic same-digest latest updates. Unchanged images skip compilation, not verification/publication, so stale latest is repaired. Native workflow serialization and a check for newer completed latest-publication steps prevent old re-runs from rolling it back, including independent app-matrix jobs and failures after a successful publication step. Explicit Wolf source overrides remain candidate-only. The manual workflow and unused gate build-variable dependency are removed. Runtime checkout fetches full history and rejects shallow provenance. Intermediate compiler caches are retained.

Local checks pass: 43 unit tests cover acquisition, stable/full/shallow history, publication failures/collisions, reuse/latest repair, PR/non-main rejection, exact-source overrides and publication order. Registry descriptor formatting was checked against the actual published runtime. Docs/schema/actionlint pass. Actual CI publication and unchanged-run verification are recorded below.

The first CI attempt caught a source-lock unit fixture reading the real shallow checkout while mocking its other external inputs. The fixture now supplies a fixed packaging identity. Full-history behavior still has a separate real-repository regression, and the runtime resolver retains its shallow-history rejection. All 43 tests also passed in an actual shallow clone after this correction.

Runtime run `38895944958` and Steam/Lutris run `38895944939` succeeded through automatic latest publication. Registry inspection confirmed the following latest digests and matching full input identities. The publisher itself checked exact immutable/latest digest equality after each write.

| Image | Immutable tag | Same-digest latest |
| --- | --- | --- |
| wolf_runtime | stable-6a5053b4ebbb-316895581a24 | sha256:8de0c342449780e390b41b6f2be575eefe3ebe320058b150e4396ab3c5d814c1 |
| wolf_steam | candidate-154b9a09b282e480 | sha256:27649e45fc7bf5ac431e6a59004418d45c3f2877ffae905cdfcf7a42419b1c72 |
| wolf_lutris | candidate-154b9a09b282e480 | sha256:2012355fad23a78bd84c3012c96dd94cdd8af3811839c02287410c43c30087ac |

Runtime repeat `38896403423` skipped compilation, reran static and vulnerability checks and republished latest at the exact same immutable digest. The intervening documentation-only commit did not change runtime identity. Application repeat `38896788999` also skipped both builds, repeated payload/session and vulnerability checks and published the exact same Steam/Lutris digests. Independent registry inspection confirmed latest/immutable equality for both apps after the repeat. Stale/missing latest and old-run ordering have unit coverage, not a deliberately destructive live registry simulation. No host rollout was performed as part of this publication cleanup.

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
