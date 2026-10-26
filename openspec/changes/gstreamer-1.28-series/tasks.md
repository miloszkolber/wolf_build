# Tasks

## 1. Replace the media series

- [x] 1.1 Add the reviewed series override beside the Wolf source hold, with the advisory cutoff and the reason, and make an undated or unverified override fail resolution.
- [x] 1.2 Extend resolver tests: the override selects the highest patch in that series, a missing tag fails, and the manifest records the divergence from Wolf's declaration.
- [x] 1.3 Confirm the compositor, interpipe and Wolf still build against `1.28.8` and that the required factories load in the final image.

## 2. Verify the payload

- [x] 2.1 Run the static final-image check and the synthetic audio chain.
- [x] 2.2 Run the isolated Intel device probe for supported hardware encoders where hardware is available.
- [x] 2.3 Record the advisory list closed by the change and any advisory that remains open against the selected series.

## 3. Acceptance and publication

- [x] 3.1 Obtain operator authorization for the media stack change before merging.
- [ ] 3.2 Publish the changed-input candidate and observe its checks and immutable tag.
- [ ] 3.3 Obtain one real TV session record for capture, audio, input and idle stop. Publication is not acceptance.
