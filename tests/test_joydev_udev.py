from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class JoydevUdevTests(unittest.TestCase):
    def test_cold_enumeration_metadata_and_matching_removal(self):
        with tempfile.TemporaryDirectory() as directory:
            include = Path(directory) / "runners"
            include.mkdir()
            (include / "joydev-udev.hpp").write_bytes(
                (ROOT / "docker/runtime/joydev-udev.hpp").read_bytes())
            binary = Path(directory) / "joydev-udev-test"
            subprocess.run(
                ["g++", "-std=c++20", "-Wall", "-Wextra", "-Werror",
                 "-I", directory, str(ROOT / "docker/runtime-tests/joydev-udev.cpp"),
                 "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
