# Evidence

The change is in the shared Heroic launch path. It reads `GAMESCOPE_HEIGHT`, which Wolf supplies for both the Gamescope and nested-Sway sessions, and adds `--force-device-scale-factor` to the existing `--console --fullscreen --no-sandbox` invocation.

The repository launch-path regression invokes `docker/apps/run.sh` with a `heroic` shim and verifies the complete argument list at session heights 2160, 1440, 1200 and 1080. The expected results are 200%, 150%, 100% and 100%. It does not render the Heroic window.

The development container ran 87 unit tests, checked 43 Markdown files, passed strict OpenSpec validation for five specifications and this change, and passed shell syntax. These checks do not establish the actual television appearance, game rendering or Moonlight acceptance.

[Application workflow 43936165395](https://github.com/miloszkolber/wolf_build/actions/runs/43936165395) built and published Heroic `41b9714e956ff42f` and `latest` at `sha256:a8016127a1055b9b28e8a15af06659bb0455644a7f17bc4a4dc9621394f37a98`. The published launcher file contains the height mapping. The host local `wolf_heroic:latest` now points at that digest; the previous digest is tagged `pre-heroic-ui`. No runtime restart was needed. Steam was rebuilt because the shared application recipe changed, but this change does not alter Steam behavior.

A real 4K television session remains the required visual acceptance before promoting the requirement to the main specification and archiving the change. The running session observed during implementation was not interrupted.
