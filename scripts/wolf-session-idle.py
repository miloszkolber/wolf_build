#!/usr/bin/env python3
"""Stop a Wolf session once its Moonlight client has been gone for a while.

Wolf pauses a session when the control channel drops and keeps the runner alive
so the client can resume. This watcher follows Wolf's own event stream and stops
a session that stays paused longer than WOLF_SESSION_IDLE_TIMEOUT seconds, so the
runner ends and the shared gate can stop the idle runtime. Set the timeout to 0
to disable it. The timeout only counts time without a client: a resume clears it.
"""
import json
import os
import select
import socket
import sys
import time
from pathlib import Path

PAUSE = "PauseStreamEvent"
RESUME = "ResumeStreamEvent"
STOP = "StopStreamEvent"
CREATED = "StreamSession"
RETRY_SECONDS = 60
RETRIES = 3
# A session restored at runtime start may be paused with no client; seed its
# deadline only when Wolf itself just started, never after a watcher-only restart.
WOLF_YOUNG_SECONDS = 60


def log(message):
    print(f"[session-idle] {message}", flush=True)


def session_of(name, data):
    if not isinstance(data, dict):
        return None
    value = data.get("client_id") if name == CREATED else data.get("session_id")
    return None if value is None else str(value)


class IdleSessions:
    def __init__(self, timeout):
        self.timeout = timeout
        self.deadlines = {}
        self.attempts = {}

    def events(self, name, data, now):
        session = session_of(name, data)
        if session is None:
            return
        if name == PAUSE:
            self.deadlines.setdefault(session, now + self.timeout)
            self.attempts.pop(session, None)
            log(f"session {session} paused; stopping it after {self.timeout}s unless the client returns")
        elif name in (RESUME, STOP):
            if self.deadlines.pop(session, None) is not None:
                log(f"session {session} {'resumed' if name == RESUME else 'stopped'}; idle deadline cleared")
            self.attempts.pop(session, None)
        elif name == CREATED:
            self.deadlines.setdefault(session, now + self.timeout)

    def arm(self, session, now):
        self.deadlines.setdefault(str(session), now + self.timeout)

    def forget(self, session):
        self.deadlines.pop(str(session), None)
        self.attempts.pop(str(session), None)

    def due(self, now):
        return sorted(session for session, deadline in self.deadlines.items() if deadline <= now)

    def retry(self, session, now):
        attempts = self.attempts.get(str(session), 0) + 1
        if attempts >= RETRIES:
            log(f"giving up on session {session} after {attempts} stop attempts")
            self.forget(session)
        else:
            self.attempts[str(session)] = attempts
            self.deadlines[str(session)] = now + RETRY_SECONDS

    def clear(self):
        self.deadlines.clear()
        self.attempts.clear()


class EventLines:
    """Server-sent-event framing, tolerant of split chunks and keepalives."""

    def __init__(self):
        self.buffer = b""
        self.name = None
        self.data = []

    def feed(self, chunk):
        self.buffer += chunk
        messages = []
        while b"\n" in self.buffer:
            raw, self.buffer = self.buffer.split(b"\n", 1)
            line = raw.decode("utf-8", "replace").rstrip("\r")
            if not line:
                if self.name and self.data:
                    messages.append((self.name, "\n".join(self.data)))
                self.name, self.data = None, []
            elif line.startswith(":"):
                continue
            elif line.startswith("event:"):
                self.name = line[6:].strip()
            elif line.startswith("data:"):
                self.data.append(line[5:].lstrip())
        return messages


def connect(socket_path, timeout=5):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(socket_path)
    return sock


def request(socket_path, method, path, body=b"", headers=()):
    sock = connect(socket_path)
    try:
        head = [f"{method} {path} HTTP/1.1", "Host: localhost", "Connection: close", *headers]
        if body:
            head.append(f"Content-Length: {len(body)}")
        sock.sendall(("\r\n".join(head) + "\r\n\r\n").encode() + body)
        chunks = []
        while True:
            data = sock.recv(65536)
            if not data:
                break
            chunks.append(data)
        raw = b"".join(chunks)
        status_line, _, rest = raw.partition(b"\r\n")
        code = int(status_line.split()[1])
        _, _, payload = rest.partition(b"\r\n\r\n")
        return code, payload
    finally:
        sock.close()


def open_events(socket_path):
    sock = connect(socket_path, timeout=30)
    sock.sendall(b"GET /api/v1/events HTTP/1.1\r\nHost: localhost\r\nAccept: text/event-stream\r\n\r\n")
    raw = b""
    while b"\r\n\r\n" not in raw:
        data = sock.recv(4096)
        if not data:
            raise OSError("API closed during event subscription")
        raw += data
    head, _, rest = raw.partition(b"\r\n\r\n")
    if b" 200 " not in head.split(b"\r\n")[0]:
        raise OSError("event subscription rejected")
    sock.settimeout(None)
    return sock, rest


def sessions(socket_path):
    code, payload = request(socket_path, "GET", "/api/v1/sessions")
    if code != 200:
        raise OSError(f"session list returned {code}")
    entries = json.loads(payload).get("sessions", [])
    return [str(entry["client_id"]) for entry in entries if entry.get("client_id")]


def stop(socket_path, session):
    body = json.dumps({"session_id": str(session)}).encode()
    code, _ = request(socket_path, "POST", "/api/v1/sessions/stop", body, ("Content-Type: application/json",))
    return code == 200


def wolf_age():
    """Seconds since the Wolf process started, or None when it is not running."""
    ticks = os.sysconf("SC_CLK_TCK")
    uptime = float(Path("/proc/uptime").read_text().split()[0])
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if (entry / "comm").read_text().strip() != "wolf":
                continue
            stat = (entry / "stat").read_text().rsplit(") ", 1)[1].split()
            return uptime - int(stat[19]) / ticks
        except (OSError, IndexError, ValueError):
            continue
    return None


def run(socket_path, timeout):
    if timeout <= 0:
        log("disabled by WOLF_SESSION_IDLE_TIMEOUT=0")
        while True:
            time.sleep(3600)
    state = IdleSessions(timeout)
    seeded = False
    while True:
        try:
            sock, rest = open_events(socket_path)
        except OSError as error:
            log(f"waiting for Wolf API at {socket_path}: {error}")
            time.sleep(2)
            continue
        log(f"watching Wolf events at {socket_path}; idle timeout {timeout}s")
        try:
            if not seeded:
                age = wolf_age()
                if age is not None and age <= WOLF_YOUNG_SECONDS:
                    try:
                        for session in sessions(socket_path):
                            state.arm(session, time.time())
                        seeded = True
                    except (OSError, ValueError) as error:
                        log(f"session list failed: {error}")
                elif age is not None:
                    seeded = True
            else:
                # A dropped stream can hide a resume; never stop on incomplete
                # information, accept that the next pause re-arms the deadline.
                state.clear()
            reader = EventLines()
            for name, data in reader.feed(rest):
                try:
                    state.events(name, json.loads(data), time.time())
                except ValueError:
                    continue
            while True:
                now = time.time()
                wait = 30.0
                if state.deadlines:
                    wait = min(wait, max(0.1, min(state.deadlines.values()) - now))
                readable, _, _ = select.select([sock], [], [], wait)
                if readable:
                    chunk = sock.recv(65536)
                    if not chunk:
                        raise ConnectionError("event stream closed")
                    for name, data in reader.feed(chunk):
                        try:
                            state.events(name, json.loads(data), time.time())
                        except ValueError:
                            continue
                for session in state.due(time.time()):
                    if stop(socket_path, session):
                        log(f"stopped session {session} after {timeout}s without a client")
                        state.forget(session)
                    else:
                        state.retry(session, time.time())
        except (OSError, ConnectionError) as error:
            log(f"event stream interrupted: {error}")
        finally:
            sock.close()


def main():
    socket_path = os.environ.get("WOLF_API_SOCKET") or str(Path(os.environ.get("XDG_RUNTIME_DIR", "/run/user/wolf")) / "wolf.sock")
    timeout = int(os.environ.get("WOLF_SESSION_IDLE_TIMEOUT", "900"))
    run(socket_path, timeout)


if __name__ == "__main__":
    main()
