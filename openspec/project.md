# Project scope

## Deliverables

| Deliverable | Owner | Proposed artifact |
| --- | --- | --- |
| Intel Wolf runtime | This repository | `ghcr.io/<owner>/wolf_runtime` |
| Universal gate | `llama_build` | Existing `ghcr.io/miloszkolber/gate` image |
| Deployment example | This repository | `compose/docker-compose.yaml` and `compose/.env.example` |
| Wolf protocol, compositor and application behavior | Games on Whales upstream | Exact resolved sources, not a maintained application fork |
| Steam and Lutris images | This repository | Minimal `wolf_steam` and `wolf_lutris` candidates, daily package/release updates and dependency inventories |
| Host rollout and acceptance | Deployment owner | Local configuration, state backups and hardware evidence |

The registry owner for the new runtime is configured at publication. Do not create a remote, registry package or credentials as part of planning.

## Planned layout

```text
docker/wolf.Dockerfile              # multi-stage supported-base Intel runtime
scripts/resolve.py                 # upstream discovery and exact input manifest
scripts/build-inputs.py            # acquisition, digest/checksum verification
scripts/check-runtime.py           # final-image static/plugin smoke checks
scripts/check-docs.mjs              # local links and documentation structure
tests/                             # resolver, manifests and assembly checks
compose/docker-compose.yaml        # published shared gate + stopped runtime
compose/.env.example               # deployment-owned paths, IDs and settings
.github/workflows/build.yml        # daily discovery, candidate build/promotion
.github/workflows/docs.yml         # documentation validation
.github/dependabot.yml             # Actions and supported Docker base updates
openspec/                          # sole documentation and planning tree
```

These are intended files, not current implementation. Each helper requires a concrete pipeline or test consumer. Avoid a rootfs collector until selected package assembly cannot satisfy the minimal-runtime contract.

## Non-goals

- No gate fork, SYCL inference dependencies, NVIDIA/AMD support or multiarchitecture images.
- No game redistribution, custom Steam/Proton fork, Decky stack or full desktop environment. Keep required 32-bit compatibility libraries.
- No new HTTP reverse proxy, streaming authentication layer or generic container orchestrator.
- No promise of higher FPS, perfect tuning, bit-reproducible builds or compatibility with every future upstream release.
