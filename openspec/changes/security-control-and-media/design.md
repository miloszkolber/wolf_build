# Design

The backport applies the complete upstream PR 558 diff to the reviewed stable source. Its shared OpenSSL error handler throws, pairing phases 1–3 report failures, outbound control errors are dropped, and audio encryption errors drop packets. In addition, a local follow-up catches errors during the pairing-request event and phase 4, passes the 16-byte tag as binary data rather than a null-terminated string, and rejects an incorrect tag length.

The Docker build verifies the full Wolf commit identifier and SHA-256 of the patched crypto, control, pairing, audio and upstream test files before `git apply --check` and application. A new Wolf commit, even one with the upstream fix, intentionally fails until the patch is reviewed or retired. The upstream clean source cache remains unchanged. Both patches, helper and test inputs are included in the existing runtime recipe identity and manifest provenance.

The build compiles and runs focused regressions against upstream crypto, pairing, control and audio code. Minimal headers stand in for unrelated types, FEC and logging. The regressions do not exercise actual REST or ENet servers, real FEC, the entire upstream test suite or a complete malformed-packet audit. Existing ENet peer matching and the pre-authentication packet parser remain unchanged. The separately identified control packet bounds and nonce reuse concerns are not fixed by PR 558 and require compatibility review.

GStreamer remains on the reviewed 1.28 series, now at a minimum of 1.28.9. The image must still pass its existing build, closure and publication gates. Rollback to an older image would restore the reported vulnerabilities and requires an explicit risk decision. Deployment and client acceptance are not performed by this change.
