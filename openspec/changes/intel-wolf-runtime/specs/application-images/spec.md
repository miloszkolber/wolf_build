## ADDED Requirements

### Requirement: Minimal maintained application images

The repository SHALL build Steam and Heroic application images independently of the streaming runtime, using a supported distribution, required amd64/i386 Intel graphics and audio client libraries, and no copied upstream desktop or multi-vendor application layer. Heroic SHALL replace the retired Lutris build and default to Console Mode for GOG-first TV use.

#### Scenario: Application assembly
- **WHEN** a Steam or Heroic image is built
- **THEN** the image preserves Wolf's per-user home, identity, display/audio sockets and input interfaces
- **AND** it excludes a separate PulseAudio server, NVIDIA integration, Decky and full desktop applications
- **AND** actual Intel/game compatibility remains a separate acceptance boundary

### Requirement: Regular tracked application updates

Application builds SHALL evaluate base, application and package dependencies daily and record exact selected artifacts and installed packages before candidate publication.

#### Scenario: Upstream or package update
- **WHEN** daily discovery or a source change triggers application assembly
- **THEN** the candidate resolves the supported base digest and stable Heroic release asset with a checked upstream SHA256, and refreshes signed distribution packages
- **AND** the candidate includes recipe identity, package inventory, SBOM and vulnerability results
- **AND** Steam client, Proton and game downloads in user state are distinguished from immutable image dependencies

#### Scenario: Heroic TV launch
- **WHEN** Wolf launches the Heroic application
- **THEN** it starts fullscreen Console Mode as the configured non-root user with a writable persistent home and working nested Wayland socket access
- **AND** retired Lutris games and configuration are not deleted or silently reinterpreted as Heroic state

#### Scenario: Failed or untrusted build
- **WHEN** acquisition, smoke or vulnerability checks fail, or a pull request runs
- **THEN** that build cannot publish a new image
- **AND** the prior accepted image and persistent user state remain unchanged

### Requirement: Accepted application digest promotion

Application images SHALL receive immutable input-identity tags and automatically advance `latest` to the same checked digest after successful default-branch builds. Publication SHALL NOT imply full-session acceptance.

#### Scenario: Successful publication
- **WHEN** application CI passes its final-image/session and vulnerability gates on the default branch
- **THEN** publication preserves the immutable input tag and advances the same digest to latest, including when the existing image was reused
- **AND** a newer successful publication cannot be replaced by an older workflow re-run

#### Scenario: Separate full application acceptance
- **WHEN** a reviewer supplies a full-acceptance record
- **THEN** it names the exact application repository and digest and covers complete streaming/game acceptance
- **AND** wrong-image or CPU-only evidence is rejected as acceptance rather than blocking normal checked-image publication
