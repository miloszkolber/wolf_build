"""End the runtime coherently if its embedded Pulse server exits.

Restarting Pulse alone loses session sinks and Wolf's routing subscription.
The gate can start a fresh runtime on the next request. Never signal a host
service or stop individual game containers outside Wolf's normal teardown.
"""
import subprocess
import sys


def pulse_failed(header, payload):
    fields = dict(item.split(":", 1) for item in payload.split() if ":" in item)
    return (header.get("eventname") in ("PROCESS_STATE_EXITED", "PROCESS_STATE_FATAL")
            and fields.get("processname") == "pulseaudio")


def run(source=sys.stdin, output=sys.stdout):
    while True:
        output.write("READY\n")
        output.flush()
        line = source.readline()
        if not line:
            return
        header = dict(item.split(":", 1) for item in line.split())
        payload = source.read(int(header["len"]))
        # Complete the event protocol before asking supervisor to shut down.
        output.write("RESULT 2\nOK")
        output.flush()
        if pulse_failed(header, payload):
            print("[audio-failure] embedded Pulse exited; shutting down runtime", file=sys.stderr, flush=True)
            subprocess.run(["supervisorctl", "-c", "/etc/supervisord.conf", "shutdown"],
                           stdout=sys.stderr, stderr=sys.stderr, check=True, timeout=10)
            return


if __name__ == "__main__":
    run()
