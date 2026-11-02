# Design

## Selection

Without an override, the resolver uses Wolf's declared series for a locked build. A reviewed series override is a small, explicit value in `scripts/resolve.py` with the reason, reviewed advisory cutoff and minimum version. While configured, it remains selected regardless of Wolf's declaration until explicitly changed or removed. Default discovery picks the highest patch returned for the selected series and verifies the tag. An explicit version must also exist and meet the series and floor. A missing declaration in a locked build, an unparseable version or a failed tag lookup fails the candidate. Advisory review is manual; resolution does not discover new advisories.

The override also records the divergence in the manifest so provenance and the build justification show that the image does not match Wolf's declared series.

## Build and closure

`compile-gstreamer.sh` already enables base, good, bad, ugly and gpl with an explicit plugin list. The series change does not alter that list. Plugin names and option spellings can move between series, so the recipe must be re-run rather than assumed, and any renamed option fails the build visibly.

The compositor and interpipe are rebuilt against the same prefix as today. Interpipe's patched test-dependency declaration must still exist exactly once; a changed upstream declaration already fails the recipe and must be re-reviewed.

`check-runtime.py --static` keeps its factory list. Additions are justified only by a Wolf pipeline requirement. The Intel device probe from the runtime documentation stays an isolated, optional check for hardware encoding, not a publication gate.

## Compatibility evidence

- A full runtime build with the selected series and the compositor, interpipe and Wolf sources at their current pins.
- Final-image static check with the library closure and factories, plus the synthetic audio conversion chain.
- An Intel device probe on the accepted target for supported hardware encoders and fallback behaviour where authorized.
- One real session on the user's TV for capture, audio, input and idle stop, recorded outside the repository. This feature-level attestation is not full codec, zero-copy or digest acceptance.

## Rollback

The previous runtime digest remains published and is the rollback reference. A Wolf source migration is independent of this change; if the series bump forces a Wolf source change, that becomes its own reviewed decision.
