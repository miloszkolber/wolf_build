import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/scan-image.sh"


class ScanTests(unittest.TestCase):
    def run_scan(self, **settings):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "candidate.tar").write_bytes(b"fixture")
            docker = root / "docker"
            docker.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
log = Path(os.environ["SCAN_LOG"])
calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
args = sys.argv[1:]
with log.open("a") as stream: stream.write(json.dumps(args) + "\\n")
if "--download-db-only" in args:
    if os.environ.get("FAIL_REFRESH") or not any("--download-db-only" in call for call in calls): sys.exit(1)
elif os.environ.get("FAIL_SCAN"): sys.exit(9)
''')
            docker.chmod(0o755)
            sleep = root / "sleep"; sleep.write_text("#!/bin/sh\nexit 0\n"); sleep.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + ":" + os.environ["PATH"], SCAN_LOG=str(root / "calls"), **settings)
            result = subprocess.run(["bash", str(SCRIPT)], cwd=root, env=env, capture_output=True, text=True)
            calls = [json.loads(line) for line in (root / "calls").read_text().splitlines()]
            caches = {argument[:-len(":/cache")] for call in calls for argument in call if argument.endswith(":/cache")}
            self.assertEqual(len(caches), 1)
            self.assertTrue(all(not Path(cache).exists() for cache in caches))
            return result, calls

    def test_refresh_retries_once_and_both_reports_share_fresh_cache(self):
        result, calls = self.run_scan()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sum("--download-db-only" in call for call in calls), 2)
        scans = [call for call in calls if "--skip-db-update" in call]
        self.assertEqual(len(scans), 2)
        self.assertIn("HIGH,CRITICAL", scans[-1])
        self.assertIn("--exit-code", scans[-1])

    def test_failed_refresh_never_runs_image_checks(self):
        result, calls = self.run_scan(FAIL_REFRESH="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(calls), 3)
        self.assertTrue(all("--download-db-only" in call for call in calls))

    def test_scan_failure_is_not_turned_into_success(self):
        result, _ = self.run_scan(FAIL_SCAN="1")
        self.assertEqual(result.returncode, 9)
