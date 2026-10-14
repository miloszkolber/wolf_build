# Tasks

## 1. Shared gate prerequisite

- [ ] 1.1 Implement and validate `llama_build`'s `universal-env-gate` record, preserving existing inference scenarios and proving environment-driven TCP/UDP handoff with no external JSON path.
- [ ] 1.2 Publish or obtain an accepted shared gate version/digest and test its exact consuming interface before the Wolf example references it.

## 2. Resolved build inputs

- [x] 2.1 Implement upstream discovery and a versioned input-manifest schema. Fixture tests cover unchanged/changed inputs, missing releases, prereleases, full source identity, API failure/rate limits and incompatible dependency sets.
- [ ] 2.2 Implement verified acquisition and license/provenance recording. Tests reject checksum mismatch, missing assets and unrecorded moving refs.
- [ ] 2.3 Establish supported-base and Intel-stack compatibility with an exact-source build. Record resolved versions and build results, not guessed package compatibility.

## 3. Complete runtime candidate

- [ ] 3.1 Build upstream Wolf/compositor/interpipe/media/audio/input components in separate stages and assemble a conservative runtime. Verify binary startup, shutdown/reaping, dynamic plugin closure and license inventory.
- [ ] 3.2 Add static and plugin smoke checks for capture/postprocessing, supported hardware encoder factories, codec parsers, Opus/audio and transport elements. Missing required factories must fail CI.
- [ ] 3.3 Remove multi-vendor/legacy/build/desktop dependency groups incrementally. Compare consistent size measurements and rerun plugin checks after each removal. Keep necessary Mesa/LLVM and supported fallback paths.
- [ ] 3.4 Verify a candidate digest on Intel hardware against the known working baseline for advertised codecs, hardware routing, zero-copy behavior, latency, quality, audio, controls, application launch and sustained sessions.

## 4. Consuming deployment

- [ ] 4.1 Author a host-neutral remote-image Compose template and `.env.example` using only the shared gate environment contract. Validate it without creating or starting runtimes and prove there is no `gate.json`, `--config` or local gate build.
- [ ] 4.2 Establish minimal device/group/socket/state requirements and writable paths. Verify cold starts, health without wake, activity protection, timeout cleanup, reconnect, idle stop and DRM release using the exact candidate images.
- [ ] 4.3 Document authorized rollout/recovery prerequisites, image identities and state-compatibility boundaries without deployment-specific measurements or paths.

## 5. Maintenance and publication

- [ ] 5.1 Add daily discovery, changed-input builds, weekly security refresh, manual exact-version candidates, dependency-update automation and failure reporting. Test selection decisions with fixtures.
- [ ] 5.2 Add workflow, Compose, docs/schema, resolver, final-image, vulnerability and SBOM checks. Verify PRs cannot publish or reach trusted Docker/GPU infrastructure.
- [ ] 5.3 Implement immutable input-hash tags and candidate-to-accepted promotion of the same tested digest. Tests cover dependency-only updates, failed acceptance, conflicting tag identity and concurrent promotion.
- [ ] 5.4 Wire trusted Intel acceptance or a recorded manual promotion gate. Demonstrate that a candidate with only hosted-runner smoke checks cannot replace `latest`.
- [ ] 5.5 Review the assembled implementation and evidence, run required checks, then sync/archive verified deltas. Do not count registry publication as host rollout.
