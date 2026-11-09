## ADDED Requirements

### Requirement: Authenticated control decryption

The runtime SHALL reject encrypted control packets when AES-GCM authentication or decryption setup fails and SHALL NOT dispatch their decrypted contents. A local security backport SHALL be limited to explicitly reviewed source and included in runtime build identity.

#### Scenario: Valid control packet
- **WHEN** an encrypted control packet has a valid tag, ciphertext and session key
- **THEN** it decrypts normally and retains existing control behavior

#### Scenario: Tampered control packet
- **WHEN** its tag or ciphertext is modified or the session key is incorrect
- **THEN** decryption fails before any decrypted content is dispatched

#### Scenario: Source changes
- **WHEN** the selected Wolf revision or reviewed patch context differs from the backport's exact input
- **THEN** the build fails until the change is reviewed and the backport updated or retired

#### Scenario: Build identity
- **WHEN** the security patch, application helper or its test harness changes
- **THEN** runtime packaging identity changes and the source manifest retains the upstream Wolf revision

### Requirement: Fail closed on crypto errors

The runtime SHALL reject failed pairing, control encryption and audio encryption operations rather than continue with output from a failed OpenSSL operation. It SHALL preserve valid pairing, control and encrypted audio behavior.

#### Scenario: Malformed pairing challenge
- **WHEN** an incomplete AES block is supplied for a pairing challenge
- **THEN** the pairing step fails and the pairing session is not advanced successfully

#### Scenario: Outgoing control encryption failure
- **WHEN** control packet encryption fails
- **THEN** the runtime does not send the failed encrypted packet

#### Scenario: Audio encryption failure
- **WHEN** audio encryption fails or its IV cannot be parsed
- **THEN** the audio packet is dropped without consuming its sequence number
