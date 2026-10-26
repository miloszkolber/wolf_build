"""Apply the embedded-audio failure policy to the pinned upstream supervisor."""
from pathlib import Path
import sys


def configure(text):
    start = text.index("[program:pulseaudio]\n")
    end = text.index("[program:wolf]\n", start)
    section = text[start:end]
    for old, new in (
        ("autorestart=true", "autorestart=false"),
        ("stdout_logfile=NONE", "stdout_logfile=/dev/fd/1"),
        ("stderr_logfile=NONE", "stderr_logfile=/dev/fd/2"),
    ):
        if section.count(old) != 1:
            raise ValueError("upstream Pulse supervision changed: " + old)
        section = section.replace(old, new)
    return text[:start] + section + text[end:]


if __name__ == "__main__":
    path = Path(sys.argv[1])
    path.write_text(configure(path.read_text()))
