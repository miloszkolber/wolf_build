# Evidence and verification status

## Source findings

Planning was grounded in the deployed upstream image's source revision `facb8e0ccd22fd6091cd904741e4dcf895e47b1b` and its `docker/wolf.Dockerfile`, `docker/gpu-drivers.Dockerfile` and `docker/gstreamer.Dockerfile`. The baseline already uses multi-stage Wolf builds, a custom GStreamer compositor, embedded PulseAudio/Supervisor and fake-udev. This is source evidence for preserving those boundaries, not a compatibility test of this project's proposed image.

Shared gate source reviewed at `llama_build` revision `b934145164d006c955636f4f6fc3b85a64b60628`: `cmd/gate/env.go` creates only the inference persistent-proxy profile, while `cmd/gate/main.go` already implements port handoff through explicit JSON configuration. Its handoff listeners bind all IPv4 interfaces independently of `GATE_HOST`. The shared change must make profile selection environment-driven, remove the external file path and preserve listener/start/activity behavior.

Host-specific image inventories, GPU measurements and deployment settings remain outside this repository. No host-specific benchmark report is copied here.

## Executed checks

- Pinned OpenSpec `1.14.1` `validate --all --strict`, run in the development container: `change/intel-wolf-runtime` passed, totals `1 passed, 0 failed`.
- The shared owner's existing `checkDocumentation` function was used as a temporary read-only checker for this repository: `13` Markdown files checked, zero failures. This establishes local-link, scenario and task structure, not a delivered repository-local checker.
- The companion shared-owner record passed its repository documentation check and pinned OpenSpec validation: `19` Markdown files checked, zero failures, and `5` OpenSpec items passed with zero failures.
- Gate-only example added in this repository: `compose/gate.compose.yaml`, `compose/gate.env.example` and `compose/README.md`. Wolf Compose validates with `docker compose --env-file compose/gate.env -f compose/gate.compose.yaml config --quiet` using the shared gate contract. The example has no `gate.json`, `--config`, build context, GPU devices or local gate implementation.
- Shared gate implementation is complete in `llama_build` with socket-level handoff evidence and a local candidate image, but no published gate version/digest has been recorded yet. The Wolf runtime image, Intel acceptance and promotion pipeline remain pending.

## Not established

No Wolf build, new image, GPU codec/zero-copy test, Moonlight session, candidate promotion or deployment has been executed for this proposal. The task ledger remains unchecked except for the gate-only example boundary. Supported-base compatibility, the minimal plugin set and automated hardware-acceptance infrastructure remain implementation work.
