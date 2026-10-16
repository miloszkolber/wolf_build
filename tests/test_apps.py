import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import io
import sys
from contextlib import redirect_stdout

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
spec = importlib.util.spec_from_file_location("apps", Path(__file__).resolve().parents[1] / "scripts/resolve-apps.py")
apps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apps)


def release():
    return {"tag_name": "v2.22.4", "assets": [{"name": "Heroic-2.22.4-linux-amd64.deb", "browser_download_url": "https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/v2.22.4/Heroic-2.22.4-linux-amd64.deb", "digest": "sha256:" + "a" * 64}]}


class ApplicationInputsTests(unittest.TestCase):
    def test_stable_release_requires_exact_asset_and_digest(self):
        self.assertEqual(apps.heroic_asset(release())["version"], "2.22.4")
        for change in ({"prerelease": True}, {"draft": True}, {"tag_name": "latest"}, {"assets": []}):
            value = release(); value.update(change)
            with self.assertRaises(ValueError): apps.heroic_asset(value)
        for field, value in (("digest", ""), ("browser_download_url", "https://attacker.invalid/heroic.deb")):
            item = release(); item["assets"][0][field] = value
            with self.assertRaises(ValueError): apps.heroic_asset(item)

    def test_base_release_recipe_and_package_change_identity(self):
        original = {"base": "a", "heroic": "2.22.4", "recipe": "a", "packages": "1.0"}
        self.assertEqual(apps.identity(original), apps.identity(dict(reversed(list(original.items())))))
        for key in original:
            changed = dict(original); changed[key] += "-changed"
            self.assertNotEqual(apps.identity(original), apps.identity(changed))

    def test_download_checksum_failure_never_replaces_existing_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "heroic.deb"
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
            (root / "docker/packages").mkdir()
            for name in ("common", "steam", "heroic"):
                (root / f"docker/packages/{name}.txt").write_text(name)
            for name in ("package-plan.sh", "resolve-packages.sh", "lock-packages.py", "install-packages.sh"):
                (root / "scripts" / name).write_text(name)
            (root / ".dockerignore").write_text("context")
            (root / "docker/apps.Dockerfile").write_text("FROM test")
            (root / "scripts/resolve-apps.py").write_text("resolver")
            (root / "scripts/resolve.py").write_text("discovery")
            script = root / "docker/apps/launch.sh"
            script.write_text("first")
            first = apps.recipe_hash(root, "steam")
            script.write_text("second")
            self.assertNotEqual(first, apps.recipe_hash(root, "steam"))
            second = apps.recipe_hash(root, "steam")
            (root / "scripts/resolve.py").write_text("changed-discovery")
            self.assertNotEqual(second, apps.recipe_hash(root, "steam"))
            third = apps.recipe_hash(root, "steam")
            (root / ".dockerignore").write_text("changed context")
            self.assertNotEqual(third, apps.recipe_hash(root, "steam"))
            steam = apps.recipe_hash(root, "steam")
            heroic = apps.recipe_hash(root, "heroic")
            (root / "docker/packages/heroic.txt").write_text("changed Heroic packages")
            self.assertEqual(steam, apps.recipe_hash(root, "steam"))
            self.assertNotEqual(heroic, apps.recipe_hash(root, "heroic"))

    def test_steam_discovery_never_resolves_or_acquires_heroic(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(apps, "discover_base_digest", return_value="sha256:" + "b" * 64), \
             patch.object(apps, "recipe_hash", return_value="c" * 64), \
             patch.object(apps, "github_api") as api, patch.object(apps, "download") as download, \
             patch("sys.argv", ["resolve-apps.py", "--app", "steam", "--output", directory]), redirect_stdout(io.StringIO()):
            apps.main()
            import json
            manifest = json.loads((Path(directory) / "manifest.json").read_text())
        self.assertNotIn("heroic", manifest["inputs"])
        self.assertNotIn("refresh", manifest["inputs"])
        self.assertNotIn("tag", manifest)
        api.assert_not_called()
        download.assert_not_called()
