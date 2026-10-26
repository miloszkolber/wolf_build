import importlib.util
import unittest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.error import URLError
import io
import json

SPEC = importlib.util.spec_from_file_location("resolve", Path(__file__).parents[1] / "scripts" / "resolve.py")
resolve = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolve)

WOLF = "a" * 40
COMP = "b" * 40
INTER = "c" * 40


def manifest(**overrides):
    values = {
        "wolf_sha": WOLF,
        "gstreamer_version": "1.26.7",
        "compositor_sha": COMP,
        "interpipe_sha": INTER,
        "media_tag": "intel-media-26.3.5",
        "vpl_tag": "intel-onevpl-26.3.5",
        "libvpl_tag": "v2.17.0",
        "base_digest": "sha256:" + "d" * 64,
    }
    values.update(overrides)
    return resolve.build_manifest(**values)


class ResolverTests(unittest.TestCase):
    def test_reviewed_series_records_divergence_and_rejects_old_advisory_basis(self):
        policy = resolve.gstreamer_policy("1.26.7")
        self.assertEqual(policy["series"], "1.28")
        self.assertEqual(policy["declared_version"], "1.26.7")
        self.assertEqual(resolve.check_gstreamer_policy("1.28.8", policy), "1.28.8")
        with self.assertRaisesRegex(ValueError, "advisory floor"):
            resolve.check_gstreamer_policy("1.28.7", policy)
        with patch.object(resolve, "GSTREAMER_REVIEW", {"series":"1.28"}):
            with self.assertRaisesRegex(ValueError, "dated advisory review"):
                resolve.gstreamer_policy("1.26.7")
        for changes in ({"reviewed_at":""}, {"reviewed_at":"2099-01-01"},
                        {"reviewed_at":"2026-01-01"}, {"reason":""}):
            with patch.object(resolve, "GSTREAMER_REVIEW", dict(resolve.GSTREAMER_REVIEW, **changes)):
                with self.assertRaises(ValueError):
                    resolve.gstreamer_policy("1.26.7")
        with patch.object(resolve, "GSTREAMER_REVIEW", None):
            self.assertEqual(resolve.gstreamer_policy("1.26.7")["series"], "1.26")

    def test_series_selects_highest_stable_patch_and_missing_tag_fails(self):
        tags = [{"name":v} for v in ("1.28.7", "1.29.0", "1.28.9-rc1", "1.28.8")]
        with patch.object(resolve, "urlopen", return_value=io.BytesIO(json.dumps(tags).encode())):
            self.assertEqual(resolve.discover_gstreamer_patch("1.28"), "1.28.8")
        with patch.object(resolve, "urlopen", side_effect=HTTPError("url",404,"missing",{},None)) as request:
            with self.assertRaises(HTTPError):
                resolve.discover_gstreamer("1.28.8", "1.28")
            self.assertEqual(request.call_count, 1)

    def test_metadata_transport_failures_retry_with_a_bound(self):
        for error in (URLError("reset"), TimeoutError("timeout")):
            with patch.object(resolve, "urlopen", side_effect=[error, io.BytesIO(b'{}')]) as request, \
                 patch.object(resolve.time, "sleep"):
                self.assertEqual(resolve.github_api("repos/example/release"), {})
                self.assertEqual(request.call_count, 2)
    def test_manifest_schema_and_stable_tag(self):
        first = manifest()
        self.assertEqual(first["version"], 1)
        self.assertEqual(first["wolf_short"], "a" * 12)
        self.assertTrue(first["candidate_tag"].startswith("stable-" + "a" * 12 + "-"))
        self.assertRegex(first["input_hash"], r"[0-9a-f]{12}")
        self.assertNotIn("gate", first["inputs"])
        self.assertEqual(first["inputs"]["intel"]["core_version"], "26.3.5")

    def test_changed_inputs_change_identity(self):
        first = manifest()
        second = manifest(gstreamer_version="1.26.6")
        self.assertNotEqual(first["input_hash"], second["input_hash"])
        self.assertNotEqual(first["candidate_tag"], second["candidate_tag"])
        third = manifest(wolf_sha="f" * 40)
        self.assertTrue(third["candidate_tag"].startswith("stable-" + "f" * 12 + "-"))

    def test_unchanged_inputs_keep_identity(self):
        self.assertEqual(manifest()["input_hash"], manifest()["input_hash"])

    def test_full_source_identity_required(self):
        with self.assertRaises(ValueError):
            manifest(wolf_sha="016b4fc")
        with self.assertRaises(ValueError):
            manifest(wolf_sha="master")
        with self.assertRaises(ValueError):
            manifest(compositor_sha="")
        with self.assertRaises(ValueError):
            manifest(interpipe_sha="not-a-sha")

    def test_missing_and_bad_releases(self):
        with self.assertRaises(ValueError):
            manifest(gstreamer_version="")
        with self.assertRaises(ValueError):
            manifest(gstreamer_version="master")
        with self.assertRaises(ValueError):
            manifest(media_tag="")
        with self.assertRaises(ValueError):
            manifest(libvpl_tag="26.3.5")
        with self.assertRaises(ValueError):
            manifest(base_digest="latest")

    def test_incompatible_dependency_sets(self):
        with self.assertRaises(ValueError):
            manifest(media_tag="intel-media-26.3.5", vpl_tag="intel-onevpl-26.3.4")
        with self.assertRaises(ValueError):
            manifest(gstreamer_version="1.24.0")

    def test_wolf_source_pin_holds_discovery(self):
        self.assertRegex(resolve.WOLF_SHA_PIN, r"[0-9a-f]{40}")
        with patch.object(resolve, "git_ls_remote", side_effect=AssertionError("a hold must not query the release channel")):
            self.assertEqual(resolve.discover_wolf_stable(), resolve.WOLF_SHA_PIN)
        self.assertTrue(manifest(wolf_sha=resolve.WOLF_SHA_PIN)["candidate_tag"].startswith("stable-" + resolve.WOLF_SHA_PIN[:12] + "-"))
        with patch.object(resolve, "WOLF_SHA_PIN", ""):
            with patch.object(resolve, "git_ls_remote", return_value={"refs/heads/stable": "e" * 40}):
                self.assertEqual(resolve.discover_wolf_stable(), "e" * 40)
        with patch.object(resolve, "WOLF_SHA_PIN", "not-a-commit"):
            with self.assertRaises(ValueError):
                resolve.discover_wolf_stable()

    def test_api_retries_then_succeeds(self):
        calls = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"{}"

        import json as json_module

        def fake_urlopen(request, timeout=30):
            calls.append(True)
            if len(calls) < 3:
                raise HTTPError(request.full_url, 503, "busy", {}, None)
            response = FakeResponse()
            response.read = lambda: json_module.dumps({"tag_name": "intel-media-26.3.5"}).encode()
            return response

        with patch.object(resolve, "urlopen", side_effect=fake_urlopen):
            with patch.object(resolve.json, "load", return_value={"tag_name": "intel-media-26.3.5"}):
                out = resolve.github_api("repos/intel/media-driver/releases/latest")
        self.assertEqual(out["tag_name"], "intel-media-26.3.5")
        self.assertEqual(len(calls), 3)

    def test_api_missing_release_fails_without_retry(self):
        calls = []

        def fake_urlopen(request, timeout=30):
            calls.append(True)
            raise HTTPError(request.full_url, 404, "missing", {}, None)

        with patch.object(resolve, "urlopen", side_effect=fake_urlopen):
            with self.assertRaises(HTTPError):
                resolve.github_api("repos/games-on-whales/wolf/releases/tags/nope")
        self.assertEqual(len(calls), 1)


    def test_runtime_packaging_ignores_application_and_docs_sources(self):
        owned = set(resolve.RUNTIME_PACKAGING)
        self.assertIn("docker/wolf.Dockerfile", owned)
        self.assertIn("scripts/resolve.py", owned)
        for app_owned in ("docker/apps.Dockerfile", "scripts/resolve-apps.py", "scripts/test-app-session.sh", "scripts/check-docs.mjs"):
            self.assertNotIn(app_owned, owned)

    def test_runtime_identity_survives_unrelated_commits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=root, text=True)
            git("init", "-q")
            for name in resolve.RUNTIME_PACKAGING:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("runtime")
            git("add", "."); git("commit", "-qm", "runtime")
            before = resolve.packaging_identity(root)
            (root / "README.md").write_text("documentation")
            (root / "docker/apps.Dockerfile").write_text("application")
            git("add", "."); git("commit", "-qm", "unrelated")
            self.assertEqual(before, resolve.packaging_identity(root))
            shallow = root / "shallow"
            git("clone", "-q", "--depth", "1", root.as_uri(), str(shallow))
            with self.assertRaisesRegex(ValueError, "full Git history"):
                resolve.packaging_identity(shallow)
            (root / "docker/wolf.Dockerfile").write_text("changed runtime")
            self.assertNotEqual(before, resolve.packaging_identity(root))


if __name__ == "__main__":
    unittest.main()
