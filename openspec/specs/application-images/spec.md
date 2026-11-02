# application-images Specification

## Purpose
Document Wolf's independently authored application container strategy. The shared Gamescope/Sway and Xwayland layer and per-application stages carry only what the games and launchers need, keep Wolf's identity/socket/input/home contracts intact, and publish only checked immutable images whose installed payload is tested on every relevant change.

## Requirements

### Requirement: Minimal maintained application images

The repository SHALL build Steam and Heroic application images independently of the streaming runtime, using a supported distribution, required amd64/i386 Intel graphics and audio client libraries, and no copied upstream desktop or multi-vendor application layer. Heroic SHALL replace the retired Lutris build and default to Console Mode for GOG-first TV use.

#### Scenario: Application assembly
- **WHEN** a Steam or Heroic image is built
- **THEN** the image preserves Wolf's per-user home, identity, display/audio sockets and input interfaces
- **AND** it excludes a separate PulseAudio server, NVIDIA integration, Decky and full desktop applications
- **AND** actual Intel/game compatibility remains a separate acceptance boundary

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

### Requirement: Steam compositor selection

Both application images SHALL default to Gamescope and SHALL retain an explicit Sway fallback. Steam SHALL enable Gamescope's Steam integration for Big Picture composition.

#### Scenario: Steam requests gamescope
- **WHEN** `RUN_GAMESCOPE` is set on the Steam runner
- **THEN** the session starts gamescope with Wolf's display width, height and refresh and runs the Steam startup under it
- **AND** the guest cursor hides after the same idle delay as the Sway session

#### Scenario: Heroic composition
- **WHEN** Heroic starts with its default environment
- **THEN** it runs through Gamescope without Steam-specific integration

#### Scenario: Default composition
- **WHEN** no compositor variable is set
- **THEN** the application starts under Gamescope

#### Scenario: Explicit fallback
- **WHEN** `RUN_GAMESCOPE` is explicitly empty
- **THEN** the application starts under nested Sway

### Requirement: Session audio defaults

Both application images SHALL route the default ALSA playback and control through PulseAudio using Wolf's supplied session server and sink. Image publication SHALL require actual default-ALSA playback from both amd64 and i386 clients reaching an isolated session sink monitor.

#### Scenario: Game uses default ALSA playback
- **WHEN** a 32-bit or 64-bit application opens the default ALSA PCM with a reachable session Pulse server
- **THEN** its non-silent samples reach the selected session sink without requiring a host ALSA sound card

### Requirement: Independent application publication

Steam and Heroic SHALL keep separate build-to-publication dependencies while sharing the maintained recipe and publisher. A failure in one application SHALL NOT block publication of the other application's checked image.

#### Scenario: One application fails its checks
- **WHEN** Heroic fails acquisition or verification and Steam passes its own required checks
- **THEN** Heroic cannot publish and Steam can still publish through its existing single publisher
