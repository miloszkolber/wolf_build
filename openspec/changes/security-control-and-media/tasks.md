# Tasks

## 1. Source repair

- [x] 1.1 Backport upstream PR 558 and its tests without switching source branches, with local binary-tag and pairing exception boundaries.
- [x] 1.2 Include the patch and harness in runtime packaging identity and fail closed on unreviewed source or patch context.
- [x] 1.3 Compile and run valid and malformed control, pairing and audio regressions against the reviewed Wolf source.
- [x] 1.4 Raise the reviewed GStreamer advisory floor to 1.28.9 and test policy enforcement.

## 2. Verification and delivery

- [x] 2.1 Run repository unit tests, documentation checks and strict OpenSpec validation after assembling the change.
- [x] 2.2 Build and test a candidate image through the existing CI pipeline, including SBOM and vulnerability gates.
- [x] 2.3 Review the assembled change and record publication separately from deployment and Moonlight/Intel acceptance.

## 3. Certificate and packet-length follow-up

- [x] 3.1 Adapt PR 566 and PR 570 against the reviewed stable source without the insecure certificate override or changing other trust rules.
- [x] 3.2 Add the changed patch, source hash and regression harness to runtime identity and build checks.
- [x] 3.3 Run focused sandbox regressions, repository unit tests, documentation checks and strict schema validation.
- [ ] 3.4 Review and run the checked-image pipeline. Record publication, deployment and real-client acceptance separately.
