import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


failure = load("audio_failure", "scripts/wolf-audio-failure.py")
supervision = load("configure_supervisor", "docker/runtime/configure-supervisor.py")


class AudioFailureTests(unittest.TestCase):
    def test_exit_and_startup_fatal_stop_runtime_but_other_processes_do_not(self):
        for event in ("PROCESS_STATE_EXITED", "PROCESS_STATE_FATAL"):
            self.assertTrue(failure.pulse_failed({"eventname": event}, "processname:pulseaudio expected:0"))
            self.assertFalse(failure.pulse_failed({"eventname": event}, "processname:wolf expected:0"))
        self.assertFalse(failure.pulse_failed({"eventname": "PROCESS_STATE_STOPPED"}, "processname:pulseaudio"))

    def test_acknowledge_before_coordinated_shutdown(self):
        payload = "processname:pulseaudio groupname:pulseaudio expected:1"
        source = io.StringIO(f"eventname:PROCESS_STATE_EXITED len:{len(payload)}\n{payload}")
        output = io.StringIO()
        def shutdown(*args, **kwargs):
            self.assertEqual(output.getvalue(), "READY\nRESULT 2\nOK")
            self.assertEqual(args[0], ["supervisorctl", "-c", "/etc/supervisord.conf", "shutdown"])
        with patch.object(failure.subprocess, "run", side_effect=shutdown):
            failure.run(source, output)

    def test_only_pulse_section_changes_and_upstream_drift_fails(self):
        text = "[program:pulseaudio]\nautorestart=true\nstdout_logfile=NONE\nstderr_logfile=NONE\n[program:wolf]\nautorestart=true\n"
        result = supervision.configure(text)
        self.assertIn("autorestart=false", result)
        self.assertIn("stderr_logfile=/dev/fd/2", result)
        self.assertTrue(result.endswith("[program:wolf]\nautorestart=true\n"))
        with self.assertRaises(ValueError):
            supervision.configure(text.replace("stderr_logfile=NONE", "stderr_logfile=/changed"))
