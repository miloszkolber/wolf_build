## MODIFIED Requirements

### Requirement: Regular tracked application updates

Application builds SHALL evaluate base, application and package dependencies weekly and record exact selected artifacts and package closures before publication. Each application SHALL have its own identity without calendar refresh salts or an unrelated application's upstream release.

#### Scenario: Upstream or package update
- **WHEN** weekly discovery or a source change triggers application assembly
- **THEN** the candidate resolves the supported base digest and stable Heroic release asset with a checked upstream SHA256, and refreshes signed distribution packages
- **AND** the candidate includes recipe identity, package inventory, SBOM and vulnerability results
- **AND** Steam client, Proton and game downloads in user state are distinguished from immutable image dependencies

#### Scenario: No relevant changes
- **WHEN** only the date, repository metadata or an unrelated package changes
- **THEN** the application reuses its immutable image and repeats required verification/scans without producing a new image

#### Scenario: Independent application release
- **WHEN** Heroic publishes a new release while Steam's resolved inputs are unchanged
- **THEN** Heroic receives a new identity and Steam retains its existing immutable image

#### Scenario: Heroic TV launch
- **WHEN** Wolf launches the Heroic application
- **THEN** it starts fullscreen Console Mode as the configured non-root user with a writable persistent home and working nested Wayland socket access
- **AND** retired Lutris games and configuration are not deleted or silently reinterpreted as Heroic state

#### Scenario: Failed or untrusted build
- **WHEN** acquisition, smoke or vulnerability checks fail, or a pull request runs
- **THEN** that build cannot publish a new image
- **AND** the prior accepted image and persistent user state remain unchanged
