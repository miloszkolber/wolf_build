## ADDED Requirements

### Requirement: Maintained media stack series

The runtime SHALL build a GStreamer series that still receives security releases, or record an operator-approved divergence from Wolf's declared series in the resolved manifest with the advisory basis for that decision.

#### Scenario: Declared series is maintained
- **WHEN** Wolf's declared GStreamer series has a release that covers the newest reviewed advisory
- **THEN** discovery selects the highest patch in that series and records no divergence

#### Scenario: Declared series has no security release
- **WHEN** a reviewed advisory names a fix only in a newer series and Wolf's declared series has no release carrying it
- **THEN** the candidate is held for an explicit reviewed series decision instead of building the unmaintained series silently
- **AND** an adopted override records the selected series, its patch, the advisory cutoff and the reason in the manifest

#### Scenario: Rebuilt plugin closure
- **WHEN** the selected series changes
- **THEN** the final image still loads the required capture, encode, audio and interpipe factories
- **AND** hardware encoding and a real session remain separate acceptance records
