import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("packages", Path(__file__).parents[1] / "scripts/lock-packages.py")
packages = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packages)

PLAN = """@@installed
base-files\tamd64\t14ubuntu1
ca-certificates\tall\t20260101
@@common
Reading package lists...
Inst base-files [14ubuntu1] (14ubuntu2 Ubuntu:26.04/resolute-updates [amd64])
Inst libpulse0:i386 (1:17.0-1 Ubuntu:26.04/resolute [i386]) []
@@steam
Inst base-files [14ubuntu1] (14ubuntu2 Ubuntu:26.04/resolute-updates [amd64])
Inst libpulse0:i386 (1:17.0-1 Ubuntu:26.04/resolute [i386])
Inst steam-installer (1.0.0.85 Ubuntu:26.04/resolute [all])
"""


class PackageIdentityTests(unittest.TestCase):
    def test_selected_closure_includes_base_security_updates_and_both_abis(self):
        closure = packages.parse_plan(PLAN, ("common", "steam"))
        self.assertEqual(closure["common"], {"base-files:amd64": "14ubuntu2", "ca-certificates": "20260101", "libpulse0:i386": "1:17.0-1"})
        self.assertEqual(closure["steam"]["steam-installer"], "1.0.0.85")

    def test_unrelated_repository_output_does_not_change_the_closure(self):
        altered = PLAN.replace("Reading package lists...", "Reading package lists...\nUnrelated repository timestamp changed")
        self.assertEqual(packages.parse_plan(PLAN, ("common", "steam")), packages.parse_plan(altered, ("common", "steam")))

    def test_incomplete_removing_or_unparseable_solver_results_fail_closed(self):
        for altered in (PLAN.replace("@@steam", "@@other"), PLAN + "Remv base-files [14ubuntu1]\n", PLAN + "Inst unsafe selection\n", PLAN + "@@common\n"):
            with self.assertRaises(ValueError): packages.parse_plan(altered, ("common", "steam"))

    def test_target_cannot_omit_an_installed_common_alternative_provider(self):
        altered = PLAN.replace("@@steam", "Inst seatd (0.9.2-2 Ubuntu:26.04/resolute [amd64])\n@@steam")
        with self.assertRaisesRegex(ValueError, "inherited common package"):
            packages.parse_plan(altered, ("common", "steam"))
        target = altered + "Inst seatd (0.9.2-2 Ubuntu:26.04/resolute [amd64])\n"
        self.assertEqual(packages.parse_plan(target, ("common", "steam"))["steam"]["seatd:amd64"], "0.9.2-2")

    def test_calendar_metadata_does_not_change_image_identity(self):
        closure = packages.parse_plan(PLAN, ("common", "steam"))
        a = {"generated": "2026-10-16", "inputs": {"app": "steam", "base": "a"}}
        b = {"generated": "2027-01-01", "inputs": {"app": "steam", "base": "a"}}
        self.assertEqual(packages.apply(a, "steam", closure)["tag"], packages.apply(b, "steam", closure)["tag"])

    def test_security_update_changes_identity_but_observation_order_does_not(self):
        closure = packages.parse_plan(PLAN, ("common", "steam"))
        original = {"inputs": {"app": "steam", "base": "a"}}
        tag = packages.apply(copy.deepcopy(original), "steam", closure)["tag"]
        reversed_closure = {key: dict(reversed(list(value.items()))) for key, value in closure.items()}
        self.assertEqual(tag, packages.apply(copy.deepcopy(original), "steam", reversed_closure)["tag"])
        changed = copy.deepcopy(closure)
        changed["steam"]["libpulse0:i386"] = "1:17.0-2"
        self.assertNotEqual(tag, packages.apply(copy.deepcopy(original), "steam", changed)["tag"])

    def test_runtime_tag_uses_resolved_package_identity(self):
        manifest = {"inputs": {"wolf": {"sha": "a" * 40}}}
        result = packages.apply(manifest, "runtime", {"build": {"gcc:amd64": "16.1"}, "runtime": {"libc6:amd64": "2.43"}})
        self.assertEqual(result["candidate_tag"], "stable-" + "a" * 12 + "-" + result["input_sha256"][:12])
