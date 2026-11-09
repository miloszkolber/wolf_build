import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wolf_security", ROOT / "scripts/apply-wolf-security.py")
security = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security)


class SecurityPatchTests(unittest.TestCase):
    def test_revision_source_and_patch_must_match_before_any_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.write_text("before\n")
            diff = root / "change.patch"
            diff.write_text("--- a/source\n+++ b/source\n@@ -1 +1 @@\n-before\n+after\n")
            expected = {"source": hashlib.sha256(source.read_bytes()).hexdigest()}
            with patch.object(security, "EXPECTED", expected):
                with self.assertRaisesRegex(ValueError, "revision"):
                    security.apply(root, "wrong", diff, diff)
                source.write_text("tampered\n")
                with self.assertRaisesRegex(ValueError, "source mismatch"):
                    security.apply(root, security.SOURCE, diff, diff)
                source.write_text("before\n")
                bad = root / "bad.patch"
                bad.write_text(diff.read_text().replace("-before", "-other"))
                with self.assertRaises(subprocess.CalledProcessError):
                    security.apply(root, security.SOURCE, bad, diff)
                self.assertEqual(source.read_text(), "before\n")
                followup = root / "followup.patch"
                followup.write_text("--- a/source\n+++ b/source\n@@ -1 +1 @@\n-after\n+final\n")
                security.apply(root, security.SOURCE, diff, followup)
                self.assertEqual(source.read_text(), "final\n")


if __name__ == "__main__":
    unittest.main()
