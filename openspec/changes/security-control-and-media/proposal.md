# Control authentication and media advisory floor

## Why

Wolf stable `db709cfd3f0f49dfd7d00495940119309692b535` logs OpenSSL errors without aborting. A forged AES-GCM control packet can therefore reach control dispatch after failed authentication. [Upstream PR 558](https://github.com/games-on-whales/wolf/pull/558) fixes this in beta, but adopting the beta branch would bring unrelated changes.

[GStreamer security advisories](https://gstreamer.freedesktop.org/security/) SA-2026-0093 through SA-2026-0101 and the SA-2026-0074 follow-up were published on 2026-11-06. [Version 1.28.9](https://gstreamer.freedesktop.org/news/?id=621) fixes the reviewed issues. The enabled plugin closure includes H.265 parsing and RTP session code affected by that review.

## What changes

- Backport the complete applicable PR 558 crypto, pairing, control and audio error handling and upstream regression tests without switching to beta. Retain the exact binary tag length fix and add catches for pairing request and phase 4 failures newly exposed by throwing crypto errors. Preserve existing session matching and connection behavior.
- Require the specifically reviewed Wolf commit and exact source-file hashes before applying the local patch. Record the patch and test harness in runtime packaging identity, and fail closed when source changes require review.
- Raise the existing reviewed GStreamer floor to 1.28.9 with the advisory cutoff and review date in the resolver. Discovery still selects actual stable patches, without a calendar rebuild salt.

## Capabilities and authority

The changed capability is `intel-runtime`. The existing shared gate remains owned by `llama_build` and is unchanged. Source delivery is authorized. Publication does not authorize deployment or paired-client changes. Final-image and real-session evidence remain separate.
