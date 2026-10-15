# Intel-only upstream-maintained Wolf runtime

## Why

The upstream general-purpose Wolf image inherits multi-vendor GPU libraries, broad media plugins and desktop utilities. Pulling its mutable tag keeps that published image refreshed but does not independently update its internal media dependencies. This project should own a narrower Intel runtime and a tested dependency-maintenance pipeline without taking ownership of Wolf's application behavior.

## What changes

- Build upstream Wolf, its custom compositor and required media plugins in separate build stages, then assemble an Intel-only runtime on a supported distribution base.
- Maintain source versions, the Intel media/graphics stack and distribution security dependencies through upstream discovery and resolved manifests.
- Preserve zero-copy capture/encoding, embedded PulseAudio, fake-udev, controller integration and upstream application-container behavior.
- Consume the universal shared gate image with environment-only `port-handoff` configuration. Eliminate the consuming `gate.json` file, mount and `--config` argument.
- Publish build-unique tags and a tested `latest`, with input provenance, licenses, SBOM and exact rollback identity.
- Build minimal Steam and Lutris application images here, with regular release/package updates and tracked dependencies. PulseAudio remains embedded in Wolf rather than becoming another image.

## Capabilities

Proposed capabilities are `intel-runtime`, `upstream-maintenance` and `gate-integration`. Gate implementation changes belong to the companion `universal-env-gate` record in `llama_build`.

## Status and authority

Implementation is authorized. The shared gate is implemented, reviewed, published and archived in its owner. Wolf source acquisition, Docker/Compose definitions and maintenance/promotion workflows are under verification. No accepted Wolf release or host rollout is established merely by delivering those files.

## Dependencies and consequential unknowns

Gate publication must precede use of environment-driven handoff. The consuming example must select an image version/digest that actually contains that contract, not assume today's `latest` already does.

Use Ubuntu 26.04 LTS as the first supported-base candidate, subject to an early build and plugin compatibility check. Exact component versions, supported Intel encoding capabilities and the viable minimal plugin set must be resolved and verified during implementation. They are not guessed from the inference stack or frozen in this prose.

Automated promotion of media-stack changes requires a trusted Intel GPU acceptance runner. Until one is available, build candidates automatically but keep `latest` at the last accepted digest and require recorded manual Intel acceptance before promotion.
