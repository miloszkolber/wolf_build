# Repository workflow

- Start with `openspec/README.md` and the active change before editing. Source/build delivery is separate from final-image verification and Intel/Moonlight acceptance.
- Keep implemented contracts in `openspec/specs/` only after delivery and verification. Keep proposed requirements, tasks and evidence in the active change.
- The shared gate implementation and publication belong to `llama_build`. Do not create a second gate implementation or publication pipeline here.
- Keep documentation and examples host-neutral. Deployment paths, group IDs, credentials and hardware measurements belong in the deployment owner's local documentation.
- Keep each prose paragraph and list item on one physical source line. Preserve structural and literal line breaks.
- Run the pinned OpenSpec validation documented in `openspec/README.md` in the development container. Distinguish schema checks from executed image, Intel GPU and Moonlight acceptance.
- Publication is not deployment. Do not start runtimes, alter paired clients or migrate persistent state without rollout authorization.
- Successful default-channel builds publish the same checked digest under both an immutable tag and `latest`. Keep one publisher per image and do not reintroduce a separate approval/promotion step. Full session acceptance remains separate.
