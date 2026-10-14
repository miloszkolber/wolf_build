# wolf_build

Plan for minimal Intel GPU Wolf streaming images, maintained from upstream releases and served on demand by the shared gate image published by [llama_build](https://github.com/miloszkolber/llama_build).

**Status: runtime planning, gate integration example available.** No Wolf runtime image or executable build workflow has been delivered. The [gate-only example](compose/README.md) requires a separately created runtime and a compatible shared gate image. Proposed runtime behavior lives in [the initial change](openspec/changes/intel-wolf-runtime/proposal.md), not in implemented specs.

## Direction

- Publish one `wolf_runtime` image for `linux/amd64`, retaining upstream Wolf, its compositor, input integration and embedded audio.
- Use a supported distribution base and an explicitly selected Intel VA-API/VPL and Mesa graphics stack. Do not transplant the SYCL inference stack.
- Discover upstream updates daily, resolve exact inputs, test candidates and publish immutable build tags plus a tested `latest`.
- Consume the existing published `gate` image. Do not fork or rebuild gate here. Gate and runtime settings come from environment variables, with no `gate.json` or `--config` mount.
- Keep Steam/Lutris application images outside this repository's build scope. Preserve their integration and state.

Start with [project scope](openspec/project.md), [design](openspec/changes/intel-wolf-runtime/design.md), [tasks](openspec/changes/intel-wolf-runtime/tasks.md) and [verification status](openspec/changes/intel-wolf-runtime/evidence.md).
