## ADDED Requirements

### Requirement: Minimal maintained application images

The repository SHALL build Steam and Lutris application images independently of the streaming runtime, using a supported distribution, required amd64/i386 Intel graphics and audio client libraries, and no copied upstream desktop or multi-vendor application layer.

#### Scenario: Application assembly
- **WHEN** a Steam or Lutris image is built
- **THEN** the image preserves Wolf's per-user home, identity, display/audio sockets, input and shared Lutris-library interfaces
- **AND** it excludes a separate PulseAudio server, NVIDIA integration, Decky and full desktop applications
- **AND** actual Intel/game compatibility remains a separate acceptance boundary

### Requirement: Regular tracked application updates

Application builds SHALL evaluate base, application and package dependencies daily and record exact selected artifacts and installed packages before candidate publication.

#### Scenario: Upstream or package update
- **WHEN** daily discovery or a source change triggers application assembly
- **THEN** the candidate resolves the supported base digest and stable Lutris release asset with a checked upstream SHA256, and refreshes signed distribution packages
- **AND** the candidate includes recipe identity, package inventory, SBOM and vulnerability results
- **AND** Steam client, Proton and game downloads in user state are distinguished from immutable image dependencies

#### Scenario: Failed or untrusted build
- **WHEN** acquisition, smoke or vulnerability checks fail, or a pull request runs
- **THEN** that build cannot publish a new image
- **AND** the prior accepted image and persistent user state remain unchanged

### Requirement: Accepted application digest promotion

Application candidates SHALL receive immutable input-identity tags and advance `latest` only through protected operator-approved same-digest promotion. A testing release SHALL NOT imply full-session acceptance.

#### Scenario: Matching full application acceptance
- **WHEN** a reviewer supplies full-acceptance evidence for application promotion
- **THEN** evidence names the exact application repository and image digest and covers complete streaming/game acceptance
- **AND** wrong-image or CPU-only evidence is rejected without changing `latest`
