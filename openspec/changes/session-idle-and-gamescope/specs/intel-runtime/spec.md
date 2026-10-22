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

#### Scenario: Restored session without a client
- **WHEN** the runtime starts and restores a paused session that no client resumes
- **THEN** the session receives the same deadline and is stopped without an application session left running

#### Scenario: Disabled
- **WHEN** `WOLF_SESSION_IDLE_TIMEOUT` is zero
- **THEN** no session stop is issued and Wolf's existing lifecycle is unchanged
