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

Publication SHALL retain immutable build-unique version tags and advance `latest` only to an operator-approved digest that passes static and vulnerability checks, without implying that pending full-session acceptance has passed.

#### Scenario: Dependency-only release
- **WHEN** accepted dependencies change but the Wolf source version does not
- **THEN** publication produces a distinct version/input-hash tag without overwriting the previous versioned image

#### Scenario: Pre-acceptance testing release
- **WHEN** the operator approves an exact candidate for testing before full game/session acceptance
- **THEN** protected promotion rechecks its payload and vulnerability gate and advances the same digest to `latest`
- **AND** it records pending full acceptance rather than creating a false accepted-session result

#### Scenario: Failed candidate
- **WHEN** payload or vulnerability checks fail, or operator approval is absent
- **THEN** `latest` remains unchanged and the failure is reported

#### Scenario: Untrusted pull request
- **WHEN** pull-request validation runs
- **THEN** it neither publishes images nor executes untrusted code on trusted Docker/GPU infrastructure
