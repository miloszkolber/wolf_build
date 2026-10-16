# Tasks

## 1. Shared gate prerequisite

- [x] 1.1 Implement and validate `llama_build`'s `universal-env-gate` record, preserving existing inference scenarios and proving environment-driven TCP/UDP handoff with no external JSON path.
- [x] 1.2 Publish or obtain an accepted shared gate version/digest and test its exact consuming interface before the Wolf example references it.

## 2. Resolved build inputs

- [x] 2.1 Implement upstream discovery and a versioned input-manifest schema. Fixture tests cover unchanged/changed inputs, missing releases, prereleases, full source identity, API failure/rate limits and incompatible dependency sets.
- [x] 2.2 Implement verified acquisition and license/provenance recording. Tests reject Git object identity mismatch, dirty cached sources and unrecorded moving refs. Source acquisition uses exact Git objects rather than pretending upstream signed archive checksums exist.
- [x] 2.3 Establish supported-base and Intel-stack compatibility with an exact-source build. Record resolved versions and build results, not guessed package compatibility.

## 3. Complete runtime candidate

- [x] 3.1 Build upstream Wolf/compositor/interpipe/media/audio/input components in separate stages and assemble a conservative runtime. Verify binary startup, shutdown/reaping, dynamic plugin closure and license inventory.
- [x] 3.2 Add static and plugin smoke checks for capture/postprocessing, supported hardware encoder factories, codec parsers, Opus/audio and transport elements. Missing required factories must fail CI.
- [ ] 3.3 Further incremental payload pruning remains deferred until game acceptance. The reduced Intel payload and same-method size comparison are verified, but further removals still require repeated plugin/game checks with Mesa/LLVM and fallbacks retained.
- [ ] 3.4 Verify a candidate digest on Intel hardware against the known working baseline for advertised codecs, hardware routing, zero-copy behavior, latency, quality, audio, controls, application launch and sustained sessions.

## 4. Consuming deployment

- [x] 4.1 Author a host-neutral remote-image Compose template and `.env.example` using only the shared gate environment contract. Validate it without creating or starting runtimes and prove there is no `gate.json`, `--config` or local gate build.
- [ ] 4.2 Establish minimal device/group/socket/state requirements and writable paths. Verify cold starts, health without wake, activity protection, timeout cleanup, reconnect, idle stop and DRM release using the exact candidate images.
- [x] 4.3 Document authorized rollout/recovery prerequisites, image identities and state-compatibility boundaries without deployment-specific measurements or paths.

## 5. Maintenance and publication

- [x] 5.1 Add daily discovery, changed-input builds, weekly security refresh, manual exact-version candidates, dependency-update automation and failure reporting. Test selection decisions with fixtures.
- [x] 5.2 Add workflow, Compose, docs/schema, resolver, final-image, vulnerability and SBOM checks. Review read-only PR permissions, default-branch publication guards and hosted-runner boundaries, and verify successful CI/publication.
- [x] 5.3 Implement immutable input-hash candidates and same-digest protected promotion. Verify dependency/acceptance rejection fixtures and registry digest preservation. Review immutable-label collision checks and per-image GitHub concurrency serialization without claiming an executed collision/race simulation.
- [x] 5.4 Wire protected manual promotion. Required reviewers and main-branch protection remain configured. Full-acceptance validation rejects CPU-only evidence. Operator-approved testing latest is separate from full acceptance.
- [ ] 5.5 Review the assembled implementation and evidence, run required checks, then sync/archive verified deltas. Do not count registry publication as host rollout.
- [x] 5.6 Simplify the build's package acquisition and Compose configuration after review. Verify unchanged-input identity, required gate settings and source checks. Keep runtime acceptance separate.

## 6. Maintained application images

- [x] 6.1 Add minimal independently authored Steam/Lutris targets on a supported base. Preserve both graphics ABIs and Wolf's identity/socket/home/input/library contracts without copying upstream desktop/Decky/NVIDIA layers.
- [x] 6.2 Add daily dependency/release discovery, checked Lutris acquisition, image package inventories, SBOM/vulnerability gates and immutable candidate publication. Test identity changes and failed acquisition. Review read-only PR authority and publication guards.
- [x] 6.3 Extend protected same-digest promotion to application images with repository-bound evidence. Reject CPU-only or wrong-image acceptance.
- [x] 6.4 Build both final images and exercise static payload, custom user identity, isolated compositor/session shutdown and injected fake-udev execution. Record actual checks, not just Dockerfile syntax.
- [ ] 6.5 Obtain operator acceptance for real Steam/Proton and Lutris native/Wine games on Intel with audio, controller/hotplug, persistence, reconnect and idle cleanup. Testing latest may precede this without claiming acceptance.

## 7. Independent release review and host test preparation

- [x] 7.1 Review current source, successful CI artifacts and exact relabeled registry digests. Repeat payload, Intel encode, app-session and stock bubblewrap checks, then rescan all three images.
- [x] 7.2 Correct runtime identity provenance so unrelated commits do not invalidate the hash. Add a real Git-history regression test.
- [x] 7.3 Promote exact checked digests to testing latest under the operator's authorization. Preserve full-acceptance validation and record actual registry results.
- [x] 7.4 Prepare the weekly maintenance prompt using the existing sibling worker contract. Do not schedule or execute it implicitly.
- [x] 7.5 Back up and deploy the host stack, preserve pairing/game state, verify cold start and return to idle, and document rollback locally.
