# upstream-maintenance Specification

## Purpose
Describe how build inputs are discovered, locked and justified. Discovery resolves exact upstream sources, base images and selected distribution package closures from signed repositories, and publication builds only when relevant inputs change.

## Requirements

### Requirement: Resolved compatible upstream inputs

The build SHALL discover updates from each declared upstream owner and acquire exact compatible inputs from a recorded manifest without re-resolving moving refs during assembly.

#### Scenario: Upstream dependency update
- **WHEN** daily discovery detects a new stable dependency or base digest
- **THEN** the resolver records the candidate's exact sources, versions, compatibility constraints and verification material before building
- **AND** incompatible or unverifiable input fails the candidate without changing the accepted image

#### Scenario: Security refresh
- **WHEN** daily discovery runs without a new Wolf release
- **THEN** supported base and selected distribution-package updates are evaluated and an actually changed input set receives its own identity
- **AND** calendar changes or unrelated repository metadata do not force a new image

#### Scenario: Locked package assembly
- **WHEN** dependency discovery selects distribution packages for a build stage or final image
- **THEN** it records the exact dependency closure including inherited base updates from signed repositories
- **AND** assembly installs those selected versions and rejects unavailable versions or a mismatched installed closure

#### Scenario: Publication justification
- **WHEN** a changed-input image is built
- **THEN** CI records changed input categories and relevant package version deltas alongside the exact manifest

### Requirement: Tested immutable publication

Publication SHALL retain immutable input-hash tags and automatically advance `latest` to the same digest that passed required checks in a default-channel build, without implying full-session acceptance.

#### Scenario: Dependency-only release
- **WHEN** accepted dependencies change but the Wolf source version does not
- **THEN** publication produces a distinct version/input-hash tag without overwriting the previous versioned image

#### Scenario: Checked default-channel release
- **WHEN** a default-channel build passes its payload/session, SBOM and vulnerability gates
- **THEN** publication preserves its immutable version tag and advances the same digest to `latest` automatically
- **AND** no separate manual promotion is required or full-acceptance result invented

#### Scenario: Unchanged inputs and stale latest
- **WHEN** the resolved immutable image already exists but latest is missing or stale
- **THEN** CI reuses and rechecks that image without recompiling and repairs latest to its exact digest

#### Scenario: Old workflow re-run
- **WHEN** a newer run already completed latest publication for the same image
- **THEN** the older re-run may retain its immutable candidate but cannot roll latest back

#### Scenario: Explicit Wolf source override
- **WHEN** a manual build selects an exact Wolf source commit
- **THEN** it publishes a checked immutable candidate without advancing the default latest channel

#### Scenario: Failed candidate
- **WHEN** payload or vulnerability checks fail
- **THEN** `latest` remains unchanged and the failure is reported

#### Scenario: Untrusted pull request
- **WHEN** pull-request validation runs
- **THEN** it neither publishes images nor executes untrusted code on trusted Docker/GPU infrastructure
