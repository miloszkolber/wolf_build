# Documentation and planning

## Owners

| Location | Content |
| --- | --- |
| [project.md](project.md) | Scope, repository boundaries and planned file layout |
| [specs/](specs/README.md) | Implemented contracts only, currently none |
| [changes/archive/2026-10-16-intel-wolf-runtime/](changes/archive/2026-10-16-intel-wolf-runtime/proposal.md) | Initial proposal, design, requirement deltas, tasks and evidence; archived 2026-10-16 after operator acceptance |
| [backlog.md](backlog.md) | Deferred work, not current implementation scope |
| [config.yaml](config.yaml) | OpenSpec context and rules |

The shared gate is owned by `llama_build`. This repository specifies its consuming interface, not duplicate gate internals or a runtime build dependency. [Acceptance records](acceptance.md) describe full session acceptance separately from automatic checked-image publication.

## Checks

Run from the repository root in the development container. OpenSpec is development tooling, not a runtime dependency. No global installation or generated agent commands are needed.

```sh
python3 -m unittest discover -s tests
bun scripts/check-docs.mjs
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.14.1 validate --all --strict
```

Structural validation establishes that the proposal is well formed, not that an image works. The active change records final-image checks, Intel probes and outstanding Moonlight acceptance separately.

Do not archive this proposal or promote deltas to main specs until implementation, review and the required acceptance are complete. Keep the same task ledger and evidence file current. Completed work will consolidate into the repository's own change history without deployment-specific reports.
