## ADDED Requirements

### Requirement: Shared environment-only gate

The deployment example SHALL consume the gate image published by `llama_build` and configure port handoff entirely through environment variables without a gate configuration file or local gate build.

#### Scenario: Wolf template configuration
- **WHEN** the example Compose configuration is rendered using its example environment
- **THEN** it selects a compatible published shared gate image with `GATE_PROFILE=port-handoff`, explicit runtime, TCP/UDP ports, activity prefixes, listener host and timeouts
- **AND** there is no `gate.json` mount, `--config` argument or gate build context
- **AND** the gate has no GPU devices while the separately created runtime owns required devices and state

### Requirement: Safe on-demand streaming lifecycle

The integration SHALL preserve cold-start TCP/UDP handoff, health without wake, readiness, active-game protection and idle device release.

#### Scenario: Cold traffic and readiness
- **WHEN** real TCP or UDP traffic arrives while the runtime is stopped
- **THEN** gate releases every handoff listener before runtime start and waits for Docker health and the configured runtime TCP listeners
- **AND** the first TCP bytes are preserved while the triggering UDP datagram is dropped for client retry

#### Scenario: Idle probe and active session
- **WHEN** a GET or HEAD health probe arrives while gate owns the listeners
- **THEN** the probe succeeds without starting the runtime
- **AND** a running application container suppresses idle shutdown once streaming is active

#### Scenario: Return to idle
- **WHEN** the idle timeout expires with no active application container
- **THEN** the runtime stops, gate reacquires its listeners and the runtime releases DRM access
- **AND** failed activity inspection cannot be interpreted as proof that no application is active
