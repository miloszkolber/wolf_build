# Documentation and planning

## Owners

| Location | Content |
| --- | --- |
| [project.md](project.md) | Scope, repository boundaries and planned file layout |
| [specs/](specs/README.md) | Implemented contracts only, currently none |
| [changes/intel-wolf-runtime/](changes/intel-wolf-runtime/proposal.md) | Initial proposal, design, requirement deltas, tasks and evidence |
| [backlog.md](backlog.md) | Deferred work, not current implementation scope |
| [config.yaml](config.yaml) | OpenSpec context and rules |

The shared gate change is owned by `llama_build` and is archived under `openspec/changes/archive/2026-10-15-universal-env-gate/`. This repository specifies the consuming deployment boundary, not duplicate gate internals. [Acceptance records](acceptance.md) describe the protected promotion boundary.

## Checks

Run from the repository root in the development container. OpenSpec is development tooling, not a runtime dependency. No global installation or generated agent commands are needed.

```sh
python3 -m unittest discover -s tests
bun scripts/check-docs.mjs
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.14.1 validate --all --strict
```

Structural validation establishes that the proposal is well formed, not that an image works. The active change records final-image checks, Intel probes and outstanding Moonlight acceptance separately.

Do not archive this proposal or promote deltas to main specs until implementation, review and the required acceptance are complete. Keep the same task ledger and evidence file current. Completed work will consolidate into the repository's own change history without deployment-specific reports.
