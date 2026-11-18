# Tasks

## 1. Implementation

- [x] 1.1 Add Heroic's Gamescope compatibility flags to the launch path without changing the running container.
- [x] 1.2 Extend the launch regression to assert the flags and the existing UI-scale behavior.
- [x] 1.3 Document the Gamescope launch flags and the next-launch scope.

## 2. Verification and delivery

- [x] 2.1 Run repository tests, documentation checks and strict OpenSpec validation.
- [x] 2.2 Build and publish the changed Heroic image through the existing application workflow.
- [ ] 2.3 Verify interface responsiveness and gamepad navigation on a real television session, then archive this change.

## 3. Reopened diagnosis after failed candidate

- [x] 3.1 Confirm the failing session uses the candidate image and flags without restarting it.
- [x] 3.2 Correct unsupported root-cause and successful-fix claims in the proposal and usage documentation.
- [x] 3.3 Measure isolated Electron and fresh-profile Heroic frame timing without production state or input devices. This fixture does not reproduce the reported stalls.
- [ ] 3.4 Capture renderer frame timing, event-loop delay, focus and Gamepad API state during the affected real-session interaction in an authorized diagnostic window.
- [ ] 3.5 Repair the evidenced failure, add a meaningful regression and repeat real launcher and game acceptance.
