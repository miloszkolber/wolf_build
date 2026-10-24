"""Check the real launcher command boundary without starting a compositor."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class GamescopeLaunchTests(unittest.TestCase):
    def launch(self, kind, refresh="120"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "gamescope").write_text("#!/bin/sh\nexit 0\n")
            capture = root / "dbus-run-session"
            capture.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
            for script in root.iterdir():
                script.chmod(0o755)
            env = dict(os.environ, PATH=f"{root}:" + os.environ["PATH"],
                       APP_KIND=kind, RUN_GAMESCOPE="1", WAYLAND_DISPLAY="wayland-1",
                       PULSE_SERVER="unused", GAMESCOPE_WIDTH="1920",
                       GAMESCOPE_HEIGHT="1080", GAMESCOPE_REFRESH=refresh)
            return subprocess.run(["bash", "docker/apps/launch.sh"], env=env,
                                  capture_output=True, text=True)

    def test_steam_enables_integration_and_preserves_display_parameters(self):
        result = self.launch("steam")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ["--", "gamescope", "-e", "-b",
                         "-W", "1920", "-H", "1080", "-r", "120", "-C", "3000",
                         "--", "/opt/app/run.sh"])

    def test_heroic_uses_gamescope_without_steam_integration(self):
        result = self.launch("heroic")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads(result.stdout)
        self.assertIn("gamescope", args)
        self.assertNotIn("-e", args)

    def test_invalid_refresh_fails_before_starting(self):
        result = self.launch("steam", "invalid")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid Gamescope refresh rate", result.stderr)
