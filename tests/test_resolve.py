import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

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
    def test_manifest_schema_and_stable_tag(self):
        first = manifest()
        self.assertEqual(first["version"], 1)
        self.assertEqual(first["wolf_short"], "a" * 12)
        self.assertTrue(first["candidate_tag"].startswith("stable-" + "a" * 12 + "-"))
        self.assertRegex(first["input_hash"], r"[0-9a-f]{12}")
        self.assertEqual(first["inputs"]["gate"]["status"], "pending-publication")
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
        with self.assertRaises(ValueError):
            manifest(gate_tag="latest", gate_digest="")

    def test_gate_resolved_pair(self):
        digest = "sha256:" + "e" * 64
        done = manifest(gate_tag="abc123def456", gate_digest=digest)
        self.assertEqual(done["inputs"]["gate"]["status"], "resolved")
        self.assertEqual(done["inputs"]["gate"]["digest"], digest)

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


if __name__ == "__main__":
    unittest.main()
