import importlib.util
import json
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("session_idle", Path(__file__).resolve().parents[1] / "scripts/wolf-session-idle.py")
idle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(idle)


class EventLineTests(unittest.TestCase):
    def test_split_chunks_keepalives_and_multiple_events(self):
        reader = idle.EventLines()
        self.assertEqual(reader.feed(b":keepalive\n\nevent: PauseStreamEvent\ndata: {\"session_id\""), [])
        messages = reader.feed(b": 7}\n\nevent: ResumeStreamEvent\r\ndata: {\"session_id\": 7}\r\n\r\n")
        self.assertEqual(messages, [("PauseStreamEvent", '{"session_id": 7}'), ("ResumeStreamEvent", '{"session_id": 7}')])

    def test_session_identifier_from_session_and_creation_events(self):
        self.assertEqual(idle.session_of("wolf::core::events::PauseStreamEvent", {"session_id": "7"}), "7")
        self.assertEqual(idle.session_of("wolf::core::events::StreamSession", {"client_id": "42"}), "42")
        self.assertIsNone(idle.session_of("wolf::core::events::ResumeStreamEvent", {}))

    def test_stream_name_matches_on_the_short_type_name(self):
        state = idle.IdleSessions(60)
        state.events("wolf::core::events::PauseStreamEvent", {"session_id": "7"}, 100)
        self.assertEqual(state.deadlines, {"7": 160})
        state.events("wolf::core::events::ResumeStreamEvent", {"session_id": "7"}, 110)
        self.assertEqual(state.deadlines, {})


class IdleSessionTests(unittest.TestCase):
    def test_pause_arms_once_and_resume_or_stop_clears(self):
        state = idle.IdleSessions(60)
        state.events("PauseStreamEvent", {"session_id": 1}, 100)
        self.assertEqual(state.deadlines, {"1": 160})
        state.events("PauseStreamEvent", {"session_id": 1}, 130)
        self.assertEqual(state.deadlines, {"1": 160})
        self.assertEqual(state.due(159), [])
        self.assertEqual(state.due(160), ["1"])
        state.events("ResumeStreamEvent", {"session_id": 1}, 161)
        self.assertEqual(state.deadlines, {})
        state.events("PauseStreamEvent", {"session_id": 1}, 200)
        state.events("StopStreamEvent", {"session_id": 1}, 210)
        self.assertEqual(state.deadlines, {})

    def test_created_session_arms_and_retries_give_up(self):
        state = idle.IdleSessions(30)
        state.events("StreamSession", {"client_id": "9"}, 10)
        self.assertEqual(state.deadlines, {"9": 40})
        state.retry("9", 50)
        self.assertEqual(state.deadlines, {"9": 110})
        state.retry("9", 110)
        self.assertEqual(state.deadlines, {"9": 170})
        state.retry("9", 170)
        self.assertEqual(state.deadlines, {})


class FakeApi:
    """Minimal Wolf unix-socket API for transport tests."""

    def __init__(self, responses):
        self.directory = tempfile.TemporaryDirectory()
        self.path = str(Path(self.directory.name) / "wolf.sock")
        self.responses = responses
        self.requests = []
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.path)
        self.server.listen(4)
        threading.Thread(target=self.serve, daemon=True).start()

    def serve(self):
        for _ in range(len(self.responses)):
            connection, _ = self.server.accept()
            with connection:
                raw = b""
                while b"\r\n\r\n" not in raw:
                    raw += connection.recv(4096)
                head, _, rest = raw.partition(b"\r\n\r\n")
                lines = head.decode().split("\r\n")
                method, target, _ = lines[0].split(" ")
                length = 0
                for line in lines[1:]:
                    if line.lower().startswith("content-length:"):
                        length = int(line.split(":", 1)[1])
                while len(rest) < length:
                    rest += connection.recv(4096)
                self.requests.append((method, target, rest[:length]))
                status, body = self.responses.pop(0)
                connection.sendall(f"HTTP/1.0 {status} OK\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body)

    def close(self):
        self.server.close()
        self.directory.cleanup()


class ApiTransportTests(unittest.TestCase):
    def test_stop_posts_the_session_id(self):
        api = FakeApi([(200, b'{"success":true}')])
        try:
            self.assertTrue(idle.stop(api.path, 12345))
            self.assertEqual(api.requests, [("POST", "/api/v1/sessions/stop", b'{"session_id": "12345"}')])
        finally:
            api.close()

    def test_stop_reports_rejection(self):
        api = FakeApi([(500, b'{"success":false}')])
        try:
            self.assertFalse(idle.stop(api.path, 1))
        finally:
            api.close()


class SubscriptionSafetyTests(unittest.TestCase):
    def test_startup_never_arms_existing_sessions_with_unknown_connection_state(self):
        # Wolf's list cannot distinguish active from paused. Starting the
        # observer after a client's Resume event must not kill that live game.
        class EndProbe(Exception):
            pass
        sock = unittest.mock.Mock()
        with patch.object(idle, "open_events", return_value=(sock, b"")), \
             patch.object(idle.select, "select", side_effect=EndProbe), \
             patch.object(idle, "request") as request:
            with self.assertRaises(EndProbe):
                idle.run("unused", 900)
            request.assert_not_called()
            sock.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
