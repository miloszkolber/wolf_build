import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("publish", Path(__file__).parents[1] / "scripts/publish.py")
publish = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publish)
IDENTITY = "a" * 64
DIGEST = "sha256:" + "b" * 64
TAG = "stable-" + "c" * 12 + "-" + IDENTITY[:12]


def descriptor(identity=IDENTITY, digest=DIGEST):
    return {"manifest": {"digest": digest}, "image": {"config": {"Labels": {"io.wolf-build.input-sha256": identity}}}}


class PublicationTests(unittest.TestCase):
    def test_build_justification_names_relevant_package_changes(self):
        before = {"base": "a", "distribution": {"steam": {"libssl:amd64": "1.0"}}}
        self.assertEqual(publish.input_changes(before, before), [])
        after = {"base": "a", "distribution": {"steam": {"libssl:amd64": "1.1"}}}
        self.assertEqual(publish.input_changes(before, after), ["steam packages (1): libssl:amd64 1.0 -> 1.1"])

    def setUp(self):
        env = {"GITHUB_REPOSITORY_OWNER": "Example", "GITHUB_REPOSITORY": "Example/wolf_build",
               "GITHUB_RUN_NUMBER": "10", "GITHUB_WORKFLOW_REF": "Example/wolf_build/.github/workflows/build.yml@refs/heads/main"}
        self.environment = patch.dict(os.environ, env)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def commands(self, *args):
        if args[:3] == ("docker", "image", "inspect"):
            return json.dumps({"io.wolf-build.input-sha256": IDENTITY})
        return "ok"

    def test_reused_image_repairs_latest_without_overwriting_immutable_tag(self):
        with patch.object(publish, "package_exists", return_value=True), patch.object(publish, "inspect", return_value=descriptor()), \
             patch.object(publish, "newer_publication_exists", return_value=False), patch.object(publish, "command", side_effect=self.commands) as command:
            self.assertEqual(publish.publish("wolf_runtime", TAG, IDENTITY, "checked:local"), DIGEST)
        calls = [call.args for call in command.call_args_list]
        self.assertFalse(any(args[:2] == ("docker", "push") for args in calls))
        create = next(args for args in calls if "create" in args)
        self.assertIn("--prefer-index=false", create)
        self.assertEqual(create[-1], "ghcr.io/example/wolf_runtime@" + DIGEST)

    def test_new_image_publishes_version_then_the_same_digest_as_latest(self):
        with patch.object(publish, "package_exists", return_value=False), patch.object(publish, "inspect", return_value=descriptor()), \
             patch.object(publish, "newer_publication_exists", return_value=False), patch.object(publish, "command", side_effect=self.commands) as command:
            publish.publish("wolf_runtime", TAG, IDENTITY, "checked:local")
        calls = [call.args for call in command.call_args_list]
        push = next(i for i, args in enumerate(calls) if args[:2] == ("docker", "push"))
        latest = next(i for i, args in enumerate(calls) if "create" in args)
        self.assertLess(push, latest)

    def test_wrong_loaded_identity_never_writes_registry(self):
        with patch.object(publish, "command", return_value="{}") as command:
            with self.assertRaisesRegex(ValueError, "collision"):
                publish.publish("wolf_runtime", TAG, IDENTITY, "wrong:local")
        self.assertEqual(command.call_count, 1)

    def test_immutable_collision_never_writes_or_advances_latest(self):
        with patch.object(publish, "package_exists", return_value=True), patch.object(publish, "inspect", return_value=descriptor("d" * 64)), \
             patch.object(publish, "command", side_effect=self.commands) as command:
            with self.assertRaisesRegex(ValueError, "collision"):
                publish.publish("wolf_runtime", TAG, IDENTITY, "checked:local")
        self.assertEqual(command.call_count, 1)

    def test_failed_push_does_not_touch_latest(self):
        def fail(*args):
            if args[:2] == ("docker", "push"):
                raise subprocess.CalledProcessError(1, args, stderr="push failed")
            return self.commands(*args)
        with patch.object(publish, "package_exists", return_value=False), patch.object(publish, "command", side_effect=fail) as command:
            with self.assertRaises(subprocess.CalledProcessError):
                publish.publish("wolf_runtime", TAG, IDENTITY, "checked:local")
        self.assertFalse(any("create" in call.args for call in command.call_args_list))

    def test_latest_digest_mismatch_fails_visibly(self):
        with patch.object(publish, "package_exists", return_value=True), \
             patch.object(publish, "inspect", side_effect=[descriptor(), descriptor(digest="sha256:" + "e" * 64)]), \
             patch.object(publish, "newer_publication_exists", return_value=False), patch.object(publish, "command", side_effect=self.commands):
            with self.assertRaisesRegex(ValueError, "latest digest"):
                publish.publish("wolf_runtime", TAG, IDENTITY, "checked:local")

    def test_old_rerun_and_explicit_version_do_not_advance_latest(self):
        for latest, newer in ((True, True), (False, False)):
            with patch.object(publish, "package_exists", return_value=True), patch.object(publish, "inspect", return_value=descriptor()), \
                 patch.object(publish, "newer_publication_exists", return_value=newer), patch.object(publish, "command", side_effect=self.commands) as command:
                publish.publish("wolf_runtime", TAG, IDENTITY, "checked:local", latest=latest)
            self.assertFalse(any("create" in call.args for call in command.call_args_list))

    def test_check_reuses_exact_digest_and_validates_identity(self):
        with patch.object(publish, "package_exists", return_value=True), patch.object(publish, "inspect", return_value=descriptor()), \
             patch.object(publish, "command", side_effect=self.commands) as command:
            self.assertTrue(publish.reuse("wolf_runtime", TAG, IDENTITY, "checked:local"))
        self.assertEqual(command.call_args_list[0].args, ("docker", "pull", "ghcr.io/example/wolf_runtime@" + DIGEST))

    def test_renamed_tag_reuses_latest_digest_for_an_unchanged_identity(self):
        reference = "ghcr.io/example/wolf_steam:latest"
        with patch.object(publish, "package_exists", return_value=True), \
             patch.object(publish, "inspect", side_effect=[None, descriptor()]), \
             patch.object(publish, "command", side_effect=self.commands) as command:
            self.assertTrue(publish.reuse("wolf_steam", IDENTITY[:16], IDENTITY, "checked:local"))
        self.assertEqual(command.call_args_list[0].args, ("docker", "pull", "ghcr.io/example/wolf_steam@" + DIGEST))
        self.assertFalse(any(args[:2] == ("docker", "pull") and reference in args[2] for args in command.call_args_list))

    def test_package_404_is_bootstrap_but_permission_errors_are_not(self):
        for status in (404, 403):
            error = subprocess.CalledProcessError(1, ["gh"], stderr=f"gh: error (HTTP {status})")
            with patch.object(publish, "gh", side_effect=[{"owner": {"type": "User"}}, error]):
                if status == 404:
                    self.assertFalse(publish.package_exists("wolf_runtime"))
                else:
                    with self.assertRaises(subprocess.CalledProcessError):
                        publish.package_exists("wolf_runtime")

    def test_missing_manifest_is_distinct_from_network_or_auth_failure(self):
        for message in ("manifest unknown", "not found", "unauthorized", "connection reset"):
            error = subprocess.CalledProcessError(1, ["docker"], stderr=message)
            with patch.object(publish, "command", side_effect=error):
                if message in ("manifest unknown", "not found"):
                    self.assertIsNone(publish.inspect("example"))
                else:
                    with self.assertRaises(subprocess.CalledProcessError):
                        publish.inspect("example")

    def test_tag_and_owner_validation(self):
        publish.validate_tag("wolf_runtime", TAG, IDENTITY)
        publish.validate_tag("wolf_steam", IDENTITY[:16], IDENTITY)
        with self.assertRaises(ValueError):
            publish.validate_tag("wolf_steam", "candidate-" + IDENTITY[:16], IDENTITY)
        with self.assertRaises(ValueError):
            publish.validate_tag("wolf_runtime", TAG, "f" * 64)
        with self.assertRaises(ValueError):
            publish.image_name("other-image")
        with self.assertRaises(ValueError):
            publish.image_name("wolf_lutris")
        self.assertEqual(publish.image_name("wolf_heroic"), "ghcr.io/example/wolf_heroic")

    def test_pr_or_non_main_cannot_publish(self):
        for ref, event in (("refs/pull/1/merge", "pull_request"), ("refs/heads/topic", "workflow_dispatch"), ("refs/heads/main", "pull_request")):
            with patch.dict(os.environ, {"GITHUB_REF": ref, "GITHUB_EVENT_NAME": event}), \
                 patch("sys.argv", ["publish.py", "publish", "wolf_runtime", TAG, IDENTITY, "checked:local"]), patch.object(publish, "publish") as writer:
                with self.assertRaisesRegex(ValueError, "trusted default-branch"):
                    publish.main()
                writer.assert_not_called()

    def test_publication_order_accounts_for_independent_matrix_jobs(self):
        newer = {"workflow_runs": [{"id": 11, "run_number": 11, "event": "push"}, {"id": 10, "run_number": 10, "event": "push"}]}
        job = {"jobs": [{"name": "publish (steam)", "conclusion": "success", "steps": [{"name": "Publish checked image and latest", "conclusion": "success"}]}]}
        with patch.dict(os.environ, {"GITHUB_WORKFLOW_REF": "Example/wolf_build/.github/workflows/apps.yml@refs/heads/main"}):
            with patch.object(publish, "gh", side_effect=[newer, job]):
                self.assertTrue(publish.newer_publication_exists("wolf_steam"))
            with patch.object(publish, "gh", side_effect=[newer, job]):
                self.assertFalse(publish.newer_publication_exists("wolf_heroic"))
            failed_post_step = copy.deepcopy(job)
            failed_post_step["jobs"][0]["conclusion"] = "failure"
            with patch.object(publish, "gh", side_effect=[newer, failed_post_step]):
                self.assertTrue(publish.newer_publication_exists("wolf_steam"))

    def test_queued_failed_or_candidate_only_newer_run_does_not_block_latest(self):
        runs = {"workflow_runs": [{"id": 11, "run_number": 11, "event": "workflow_dispatch"}, {"id": 10, "run_number": 10, "event": "push"}]}
        for jobs in ([], [{"name": "publish", "steps": []}], [{"name": "publish", "steps": [{"name": "Publish exact-version candidate", "conclusion": "success"}]}]):
            with patch.object(publish, "gh", side_effect=[runs, {"jobs": jobs}]):
                self.assertFalse(publish.newer_publication_exists("wolf_runtime"))

    def test_order_lookup_paginates_and_api_errors_fail_closed(self):
        with patch.object(publish, "gh", side_effect=[{"workflow_runs": [{"id": 11, "run_number": 11, "event": "push"}]}, {"jobs": []}, {"workflow_runs": []}]) as gh:
            self.assertFalse(publish.newer_publication_exists("wolf_runtime"))
            self.assertIn("page=2", gh.call_args.args[0])
        with patch.object(publish, "gh", side_effect=subprocess.CalledProcessError(1, ["gh"], stderr="unavailable")):
            with self.assertRaises(subprocess.CalledProcessError):
                publish.newer_publication_exists("wolf_runtime")
