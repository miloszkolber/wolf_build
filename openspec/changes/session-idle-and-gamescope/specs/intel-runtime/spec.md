## ADDED Requirements

### Requirement: Idle session stop

The runtime SHALL stop a stream session whose Moonlight client has been gone longer than a configured interval, while keeping the session resumable during that interval. The interval SHALL be configurable through `WOLF_SESSION_IDLE_TIMEOUT` and SHALL default to 900 seconds. A value of zero SHALL disable the stop.

#### Scenario: Client disappears
- **WHEN** the Moonlight control channel drops and no resume arrives within the configured interval
- **THEN** the runtime fires its normal stop path for that session and the application container exits
- **AND** the shared gate can stop the runtime once no application container remains

#### Scenario: Client returns
- **WHEN** the same client resumes before the interval expires
- **THEN** the pending stop is cancelled and the session continues without restarting the runner

#### Scenario: Observer starts after a client connects
- **WHEN** a session exists before the event subscription begins and its connection state is unknown
- **THEN** the watcher does not invent an idle deadline for that session

#### Scenario: Disabled
- **WHEN** `WOLF_SESSION_IDLE_TIMEOUT` is zero
- **THEN** no session stop is issued and Wolf's existing lifecycle is unchanged

### Requirement: Coherent embedded audio failure

The runtime SHALL retain embedded PulseAudio diagnostics and SHALL shut down coherently through supervisor if the embedded audio process exits or cannot start. It SHALL NOT restart Pulse alone while retaining Wolf's stale connections and virtual-sink state. Runtime health SHALL require a responsive Pulse server in addition to the existing Wolf readiness checks.

#### Scenario: Embedded server exits
- **WHEN** the embedded PulseAudio process exits while the runtime is active
- **THEN** supervisor initiates runtime shutdown and Wolf receives its normal graceful stop signal
- **AND** a subsequent gate request can start a fresh runtime instead of reusing stale audio state

#### Scenario: Audio server is unreachable
- **WHEN** Wolf is listening but its Pulse server does not answer a bounded query
- **THEN** the runtime health check fails
