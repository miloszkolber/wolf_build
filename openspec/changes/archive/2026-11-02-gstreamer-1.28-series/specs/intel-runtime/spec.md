## ADDED Requirements

### Requirement: Maintained media stack series

The resolved runtime manifest SHALL identify the selected GStreamer series and version. A reviewed series override SHALL record Wolf's declared version, the selected series, the advisory cutoff, minimum version, review date and reason. The resolver SHALL enforce the reviewed minimum. New source-built media advisories require manual review and are not automatically detected by the distribution-package scan.

#### Scenario: No series override
- **WHEN** a locked build is resolved without a series override
- **THEN** the resolver uses Wolf's declared series and records the declaration in the manifest
- **AND** default discovery selects the highest stable patch returned for that series and verifies its tag

#### Scenario: Reviewed series override
- **WHEN** a reviewed override selects a series and minimum version
- **THEN** resolution records the review metadata and rejects a version below the minimum or outside the selected series
- **AND** it rejects a missing reason, invalid review dates or a review predating its advisory cutoff
- **AND** the configured override remains selected regardless of Wolf's declared series until it is explicitly changed or removed

#### Scenario: Explicit patch
- **WHEN** an explicit GStreamer version is supplied
- **THEN** resolution verifies that its tag exists and that it satisfies the selected series and reviewed minimum

#### Scenario: Rebuilt plugin closure
- **WHEN** the selected series changes
- **THEN** the final image still loads the required capture, encode, audio and interpipe factories
- **AND** hardware encoding and a real session remain separate acceptance records
