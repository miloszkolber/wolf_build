import importlib.util
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
import tempfile
import subprocess
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import resolve
spec=importlib.util.spec_from_file_location("acquisition",Path(__file__).resolve().parents[1]/"scripts/build-inputs.py")
acquisition=importlib.util.module_from_spec(spec)
spec.loader.exec_module(acquisition)


class LockedInputsTests(unittest.TestCase):
    def test_git_network_retry_has_per_operation_deadline(self):
        with patch.object(acquisition.subprocess, "check_output", side_effect=[subprocess.TimeoutExpired("git",600), "done"]) as run, \
             patch.object(acquisition.time, "sleep"):
            self.assertEqual(acquisition.git("fetch", "origin", "a"*40), "done")
            self.assertEqual(run.call_count, 2)
            self.assertEqual(run.call_args.kwargs["timeout"], 600)

    def test_acquisition_rejects_git_object_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp);(target/".git").mkdir()
            with patch.object(acquisition,"git",side_effect=["","b"*40,"","","b"*40]):
                with self.assertRaisesRegex(ValueError,"identity mismatch"):
                    acquisition.acquire({"url":"https://github.com/a/b.git","sha":"a"*40},target)

    def test_acquisition_rejects_unrecorded_cache_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp);(target/".git").mkdir()
            with patch.object(acquisition,"git",return_value=" M source.cpp"):
                with self.assertRaisesRegex(ValueError,"unrecorded modifications"):
                    acquisition.acquire({"url":"https://github.com/a/b.git","sha":"a"*40},target)

    def test_selected_revision_can_advance_pinned_submodule(self):
        state={"updated":False,"head":"b"*40}
        def git(*args,**kwargs):
            if args[0]=="status":
                return "" if "--ignore-submodules=all" in args or state["updated"] else " M child"
            if args[0]=="rev-parse": return state["head"]
            if args[0]=="checkout": state["head"]="a"*40
            if args[:2]==("submodule","update"): state["updated"]=True
            if args[:2]==("submodule","status"): return "a"*40+" child"
            if args[:2]==("submodule","foreach"): return "child\t"+"a"*40
            return ""
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp);(target/".git").mkdir()
            with patch.object(acquisition,"git",side_effect=git):
                result=acquisition.acquire({"url":"https://github.com/a/b.git","sha":"a"*40},target)
        self.assertEqual(result,{"child":"a"*40})

    def test_submodule_identity_ignores_descriptive_tags_but_tracks_commits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "child"; child.mkdir()
            parent = root / "parent"; parent.mkdir()
            def git(path, *args):
                return subprocess.check_output(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args],
                                               cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
            git(child, "init", "-q", "-b", "main")
            (child / "file").write_text("original")
            git(child, "add", "."); git(child, "commit", "-qm", "initial")
            git(parent, "init", "-q", "-b", "main")
            git(parent, "-c", "protocol.file.allow=always", "submodule", "add", str(child), "dependency with spaces")
            git(parent, "commit", "-qam", "initial")
            source = {"url":"https://github.com/example/fixture.git", "sha":git(parent,"rev-parse","HEAD")}
            before = acquisition.acquire(source, parent)
            dependency = parent / "dependency with spaces"
            git(dependency, "tag", "description-only")
            self.assertEqual(before, acquisition.acquire(source, parent))
            self.assertEqual(before, {"dependency with spaces":git(dependency,"rev-parse","HEAD")})
            (dependency / "file").write_text("changed")
            git(dependency, "commit", "-qam", "new source")
            git(parent, "add", "."); git(parent, "commit", "-qm", "advance dependency")
            source["sha"] = git(parent, "rev-parse", "HEAD")
            self.assertNotEqual(before, acquisition.acquire(source, parent))

    def test_rate_limit_failure_never_falls_back(self):
        with patch.object(resolve,"urlopen",side_effect=HTTPError("url",429,"limited",{},None)) as request,patch.object(resolve.time,"sleep"):
            with self.assertRaises(HTTPError): resolve.github_api("repos/a/b/releases/latest")
            self.assertEqual(request.call_count,3)

    def test_reject_unsafe_or_unlocked_sources(self):
        for source in ({"url":"file:///private/key","sha":"a"*40},{"url":"https://github.com/a/b.git","sha":"HEAD"},{"url":"https://attacker.invalid/a/b","sha":"a"*40}):
            with self.assertRaises(ValueError): acquisition.validate_source(source)
        acquisition.validate_source({"url":"https://github.com/a/b.git","sha":"a"*40})

    def test_release_channels_reject_prereleases(self):
        for key in range(3):
            releases=[{"tag_name":"intel-media-26.3.5"},{"tag_name":"intel-onevpl-26.3.5"},{"tag_name":"v2.17.0"}]
            releases[key]["prerelease"]=True
            with patch.object(resolve,"github_api",side_effect=releases):
                with self.assertRaises(ValueError): resolve.discover_intel()

    def test_lock_expands_declared_compatibility_and_unpinned_cmake(self):
        inputs={"wolf":{"sha":"a"*40},"gstreamer":{"version":"1.28.8"},"interpipe":{"sha":"b"*40},"intel":{"media_driver":"intel-media-26.3.5","vpl_gpu_rt":"intel-onevpl-26.3.5","libvpl":"v2.17.0"}}
        original=copy.deepcopy(inputs)
        def api(path):
            if "releases/tags" in path: return {"body":"intel-gmmlib-22.10.2 intel/libva/releases/tag/2.24.1 intel/libvpl/releases/tag/v2.17.0"}
            return {"tree":[{"path":"CMakeLists.txt"}]}
        def raw(repo,sha,path):
            return {"docker/wolf.Dockerfile":"ARG RUST_VERSION=1.96.0\ngit checkout 016b4fc\ncargo install cargo-c@0.10.23", "docker/gstreamer.Dockerfile":"ARG GSTREAMER_VERSION=1.26.7", "CMakeLists.txt":"FetchContent_Declare(mdns_cpp GIT_REPOSITORY https://github.com/games-on-whales/mdns_cpp.git)"}[path]
        with patch.object(resolve,"source_commit",return_value="c"*40),patch.object(resolve,"github_api",side_effect=api),patch.object(resolve,"raw",side_effect=raw),patch.object(resolve,"hub_digest",return_value="sha256:"+"d"*64):
            with patch.object(resolve,"datetime") as clock, patch.object(resolve,"packaging_identity",return_value={"sha256":"e"*64,"revision":"f"*40,"dirty":False}):
                clock.now.return_value=datetime(2026,10,15,8,tzinfo=timezone.utc)
                manifest=resolve.lock_sources({"inputs":inputs})
                clock.now.return_value=datetime(2026,10,16,9,tzinfo=timezone.utc)
                unchanged=resolve.lock_sources({"inputs":copy.deepcopy(original)})
                clock.now.return_value=datetime(2026,10,22,8,tzinfo=timezone.utc)
                refreshed=resolve.lock_sources({"inputs":copy.deepcopy(original)})
        self.assertEqual(manifest["input_hash"],unchanged["input_hash"])
        self.assertEqual(manifest["input_hash"],refreshed["input_hash"])
        self.assertNotIn("refresh_week", inputs)
        self.assertNotIn("distribution_snapshot",inputs)
        self.assertEqual(manifest["version"],2)
        self.assertEqual(inputs["cmake_sources"]["MDNS_CPP"],"wolf-mdns_cpp")
        self.assertEqual(inputs["sources"]["wolf-mdns_cpp"]["sha"],"c"*40)
        self.assertEqual(inputs["sources"]["gmmlib"]["ref"],"intel-gmmlib-22.10.2")
        self.assertIn("digest",inputs["toolchain"])
        self.assertEqual(inputs["gstreamer"]["declared_version"], "1.26.7")
        self.assertEqual(inputs["gstreamer"]["series"], "1.28")
        self.assertEqual(inputs["gstreamer"]["review"]["minimum_version"], "1.28.8")

    def test_base_must_resolve_for_target_architecture(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return json.dumps({"images":[{"architecture":"arm64","os":"linux","digest":"sha256:"+"a"*64}]}).encode()
        with patch.object(resolve,"urlopen",return_value=Response()):
            with self.assertRaises(ValueError): resolve.discover_base_digest()
