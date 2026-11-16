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

### Requirement: Paired-client certificate verification

The runtime SHALL reject client certificates with an unknown issuer during paired-client authorization. It SHALL retain verification anchored at a paired certificate, including the existing partial-chain and certificate validity-time behavior, without an override that permits unknown issuers.

#### Scenario: Paired certificate
- **WHEN** a client presents its paired certificate
- **THEN** its certificate passes verification against that paired record

#### Scenario: Unknown issuer
- **WHEN** an unpaired client presents a certificate naming an unknown issuer
- **THEN** it does not match a paired record, regardless of the insecure upstream compatibility environment variable

### Requirement: Received control packet bounds

The runtime SHALL validate a received control header before reading its type and SHALL reject encrypted packets whose declared bytes do not fit the received buffer or cannot contain an inner control header.

#### Scenario: Truncated or undersized encrypted packet
- **WHEN** a packet is shorter than its declared length or its encrypted payload is shorter than a control header
- **THEN** it is dropped before decryption and control dispatch

#### Scenario: Valid encrypted packet
- **WHEN** an encrypted control packet contains a complete header and payload and authenticates successfully
- **THEN** it retains existing control behavior
