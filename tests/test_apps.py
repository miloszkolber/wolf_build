import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import io
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
spec = importlib.util.spec_from_file_location("apps", Path(__file__).resolve().parents[1] / "scripts/resolve-apps.py")
apps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apps)


def release():
    return {"tag_name": "v0.5.22", "assets": [{"name": "lutris_0.5.22_all.deb", "browser_download_url": "https://github.com/lutris/lutris/releases/download/v0.5.22/lutris_0.5.22_all.deb", "digest": "sha256:" + "a" * 64}]}


class ApplicationInputsTests(unittest.TestCase):
    def test_stable_release_requires_exact_asset_and_digest(self):
        self.assertEqual(apps.lutris_asset(release())["version"], "0.5.22")
        for change in ({"prerelease": True}, {"draft": True}, {"tag_name": "latest"}, {"assets": []}):
            value = release(); value.update(change)
            with self.assertRaises(ValueError): apps.lutris_asset(value)
        for field, value in (("digest", ""), ("browser_download_url", "https://attacker.invalid/lutris.deb")):
            item = release(); item["assets"][0][field] = value
            with self.assertRaises(ValueError): apps.lutris_asset(item)

    def test_base_release_recipe_and_refresh_change_identity(self):
        original = {"base": "a", "lutris": "0.5.22", "recipe": "a", "refresh": "2026-10-15"}
        self.assertEqual(apps.identity(original), apps.identity(dict(reversed(list(original.items())))))
        for key in original:
            changed = dict(original); changed[key] += "-changed"
            self.assertNotEqual(apps.identity(original), apps.identity(changed))

    def test_download_checksum_failure_never_replaces_existing_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "lutris.deb"
            target.write_bytes(b"previous")
            with patch.object(apps, "urlopen", return_value=io.BytesIO(b"wrong")):
                with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                    apps.download({"url": "https://example.invalid", "sha256": "a" * 64}, target)
            self.assertEqual(target.read_bytes(), b"previous")
            self.assertFalse(target.with_suffix(".partial").exists())

    def test_application_recipe_hash_includes_nested_launch_scripts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docker/apps").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / ".dockerignore").write_text("context")
            (root / "docker/apps.Dockerfile").write_text("FROM test")
            (root / "scripts/resolve-apps.py").write_text("resolver")
            (root / "scripts/resolve.py").write_text("discovery")
            script = root / "docker/apps/launch.sh"
            script.write_text("first")
            first = apps.recipe_hash(root)
            script.write_text("second")
            self.assertNotEqual(first, apps.recipe_hash(root))
            second = apps.recipe_hash(root)
            (root / "scripts/resolve.py").write_text("changed-discovery")
            self.assertNotEqual(second, apps.recipe_hash(root))
            third = apps.recipe_hash(root)
            (root / ".dockerignore").write_text("changed context")
            self.assertNotEqual(third, apps.recipe_hash(root))
