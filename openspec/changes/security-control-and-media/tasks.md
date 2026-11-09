# Tasks

## 1. Source repair

- [x] 1.1 Backport upstream PR 558 and its tests without switching source branches, with local binary-tag and pairing exception boundaries.
- [x] 1.2 Include the patch and harness in runtime packaging identity and fail closed on unreviewed source or patch context.
- [x] 1.3 Compile and run valid and malformed control, pairing and audio regressions against the reviewed Wolf source.
- [x] 1.4 Raise the reviewed GStreamer advisory floor to 1.28.9 and test policy enforcement.

## 2. Verification and delivery

- [x] 2.1 Run repository unit tests, documentation checks and strict OpenSpec validation after assembling the change.
- [ ] 2.2 Build and test a candidate image through the existing CI pipeline, including SBOM and vulnerability gates.
- [ ] 2.3 Review the assembled change and record publication separately from deployment and Moonlight/Intel acceptance.
