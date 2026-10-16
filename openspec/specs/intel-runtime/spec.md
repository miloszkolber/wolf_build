# intel-runtime Specification

## Purpose
Specify the Intel streaming runtime image contract: Intel VA/VPL and Mesa rendering components, explicitly selected GStreamer plugin closure, embedded audio and input integration, and checked publication identity. Kernel drivers and firmware stay host responsibilities.

## Requirements

### Requirement: Supported Intel runtime

The runtime image SHALL build exact upstream sources on a supported distribution base and retain the Intel graphics/media dependencies needed for capture and supported encoding without unrelated vendor runtimes or build tooling.

#### Scenario: Final image inventory
- **WHEN** the resolved candidate image is inspected and its required plugin factories are loaded
- **THEN** Wolf, the compositor, audio/input components and Intel capture/encoding dependencies are present without missing-library errors
- **AND** compilers, source trees, NVIDIA NVRTC/CUDA and AMD-specific driver payloads are absent
- **AND** its base/source/package identities and licenses are available in provenance

### Requirement: Streaming integration parity

The runtime SHALL preserve upstream pairing, application launch, audio and input behavior and establish hardware encoding on accepted Intel targets.

#### Scenario: Accepted Intel session
- **GIVEN** an advertised supported codec and an exact candidate digest
- **WHEN** Moonlight launches a supported application and streams with the baseline settings
- **THEN** the session uses the intended Intel hardware path without hidden software fallback and passes recorded latency, quality and dropped-frame tolerances
- **AND** pairing/reconnect, audio, keyboard/mouse/controller events and application exit work

#### Scenario: Unsupported capability
- **WHEN** the target does not advertise a codec capability
- **THEN** its acceptance record identifies that codec as not applicable with capability evidence instead of claiming a passing hardware test
