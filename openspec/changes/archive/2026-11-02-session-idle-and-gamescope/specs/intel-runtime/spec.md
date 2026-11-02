## ADDED Requirements

### Requirement: Idle session stop

The runtime SHALL track observed session creation and pause events and request a normal session stop after a configured interval unless an observed resume or stop cancels the deadline. The interval SHALL be configurable through `WOLF_SESSION_IDLE_TIMEOUT` and SHALL default to 900 seconds. A value of zero SHALL disable the stop. The watcher SHALL fail open across event subscription gaps and SHALL NOT infer connection state for existing sessions.

#### Scenario: Client disappears
- **WHEN** the watcher observes the Moonlight control channel pause and the event subscription remains uninterrupted without a resume or stop until the configured interval expires
- **THEN** the runtime requests its normal stop path for that session
- **AND** a successful stop ends the application container
- **AND** the shared gate can stop the runtime once no application container remains

#### Scenario: Subscription interrupted
- **WHEN** the event subscription is interrupted, possibly hiding a pause or resume
- **THEN** the watcher clears pending deadlines rather than stopping a potentially active session
- **AND** an unobserved pause can leave the session running until another observed pause or explicit quit

#### Scenario: Stop request fails
- **WHEN** a stop request fails while the event subscription remains healthy
- **THEN** the watcher retries a bounded number of times and gives up if those attempts fail

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
