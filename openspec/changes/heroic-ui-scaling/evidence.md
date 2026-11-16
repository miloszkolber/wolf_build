# Evidence

The change is in the shared Heroic launch path. It reads `GAMESCOPE_HEIGHT`, which Wolf supplies for both the Gamescope and nested-Sway sessions, and adds `--force-device-scale-factor` to the existing `--console --fullscreen --no-sandbox` invocation.

The repository launch-path regression invokes `docker/apps/run.sh` with a `heroic` shim and verifies the complete argument list at session heights 2160, 1440, 1200 and 1080. The expected results are 200%, 150%, 100% and 100%. It does not render the Heroic window.

The development container ran 87 unit tests, checked 43 Markdown files, passed strict OpenSpec validation for five specifications and this change, and passed shell syntax. These checks do not establish the actual television appearance, game rendering or Moonlight acceptance.

The application workflow has not yet built this change. A real 4K television session remains the required visual acceptance before promoting the requirement to the main specification and archiving the change.
