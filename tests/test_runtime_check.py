import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import subprocess

spec = importlib.util.spec_from_file_location("runtime_check", Path(__file__).resolve().parents[1] / "scripts/check-runtime.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def table(*rows):
    header = "  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode\n"
    return header + "".join(f"   {index}: {row}\n" for index, row in enumerate(rows))


class HealthCheckTests(unittest.TestCase):
    def test_only_listening_sockets_count(self):
        with tempfile.TemporaryDirectory() as directory:
            tcp = Path(directory) / "tcp"
            tcp.write_text(table("00000000:BB70 00000000:0000 0A", "00000000:BB75 0100007F:1F90 01", "00000000:BB8A 00000000:0000 0A", "broken"))
            self.assertEqual(check.listening_ports((tcp, Path(directory) / "missing")), {47984, 48010})

    def test_readiness_needs_every_listener(self):
        with patch.object(check, "wolf_running", return_value=True), \
                patch.object(check, "listening_ports", return_value={47984, 47989, 48010}), \
                patch.object(check.subprocess, "run", return_value=SimpleNamespace(returncode=0)):
            self.assertTrue(check.health())
        with patch.object(check, "wolf_running", return_value=True), \
                patch.object(check, "listening_ports", return_value={47984, 47989}):
            self.assertFalse(check.health())
        with patch.object(check, "wolf_running", return_value=False), \
                patch.object(check, "listening_ports", return_value={47984, 47989, 48010}):
            self.assertFalse(check.health())

    def test_health_never_dials_wolf_servers(self):
        self.assertFalse(hasattr(check, "socket"))

    def test_open_ports_do_not_hide_dead_or_unresponsive_audio(self):
        with patch.object(check, "wolf_running", return_value=True), \
                patch.object(check, "listening_ports", return_value={47984, 47989, 48010}):
            with patch.object(check.subprocess, "run", return_value=SimpleNamespace(returncode=1)):
                self.assertFalse(check.health())
            with patch.object(check.subprocess, "run", side_effect=subprocess.TimeoutExpired("pactl", 1)):
                self.assertFalse(check.health())


if __name__ == "__main__":
    unittest.main()
