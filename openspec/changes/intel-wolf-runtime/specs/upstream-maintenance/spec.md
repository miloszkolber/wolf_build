## ADDED Requirements

### Requirement: Resolved compatible upstream inputs

The build SHALL discover updates from each declared upstream owner and acquire exact compatible inputs from a recorded manifest without re-resolving moving refs during assembly.

#### Scenario: Upstream dependency update
- **WHEN** daily discovery detects a new stable dependency or base digest
- **THEN** the resolver records the candidate's exact sources, versions, compatibility constraints and verification material before building
- **AND** incompatible or unverifiable input fails the candidate without changing the accepted image

#### Scenario: Security refresh
- **WHEN** the weekly refresh runs without a new Wolf release
- **THEN** supported distribution/base security updates are evaluated and any resulting new input set receives its own candidate identity

### Requirement: Tested immutable publication

Publication SHALL retain immutable build-unique version tags and advance `latest` only to the same digest that passed required static and Intel integration acceptance.

#### Scenario: Dependency-only release
- **WHEN** accepted dependencies change but the Wolf source version does not
- **THEN** publication produces a distinct version/input-hash tag without overwriting the previous versioned image

#### Scenario: Hardware acceptance unavailable or failed
- **WHEN** a candidate has only hosted-runner smoke evidence or fails Intel acceptance
- **THEN** the previous `latest` digest remains unchanged and the candidate's incomplete or failing status is reported

#### Scenario: Untrusted pull request
- **WHEN** pull-request validation runs
- **THEN** it neither publishes images nor executes untrusted code on trusted Docker/GPU infrastructure
