"""Final-image checks. Static plugin checks are not hardware acceptance."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


def run(*args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True, timeout=30)


def static():
    manifest = json.loads(Path("/licenses/manifest.json").read_text())
    if manifest.get("version") != 2:
        raise ValueError("missing resolved input lock")
    problems = []
    for path in [Path("/wolf/wolf"), Path("/wolf/fake-udev"), *Path("/opt/wolf-runtime/lib").rglob("*.so*")]:
        if path.is_symlink() or not path.is_file(): continue
        with path.open("rb") as binary:
            if binary.read(4) != b"\x7fELF": continue
        result=subprocess.run(["ldd",str(path)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30)
        missing=[line.strip() for line in result.stdout.splitlines() if "not found" in line]
        if missing: problems.append(str(path)+": "+"; ".join(missing))
        elif result.returncode and not (path==Path("/wolf/fake-udev") and "not a dynamic executable" in result.stdout):
            problems.append("cannot inspect library closure: "+str(path)+"\n"+result.stdout)
    if problems: raise ValueError("missing libraries:\n"+"\n".join(problems))
    # Upstream intentionally links this helper statically for other app images.
    run("/wolf/fake-udev","--help")
    # Software factories are device-independent. VA and QSV factories are often
    # registered only after driver/device probing, so require their plugins here.
    for element in ("appsrc", "appsink", "videoconvert", "videoscale", "audioconvert", "audiorate", "audioresample", "opusenc", "opusdec", "pulsesrc", "udpsink", "rtph264pay", "h264parse", "h265parse", "av1parse", "x264enc", "x265enc", "av1enc", "interpipesrc", "interpipesink", "waylanddisplaysrc"):
        run("gst-inspect-1.0",element)
    for plugin in ("va", "qsv"):
        run("gst-inspect-1.0",plugin)
    # Exercise Wolf's default audio conversion/encoding chain, not just isolated
    # factories. The synthetic source/sink require no sound server or devices.
    run("gst-launch-1.0", "-q", "audiotestsrc", "num-buffers=8", "!",
        "audio/x-raw,rate=48000,channels=2", "!", "queue", "max-size-buffers=3",
        "leaky=downstream", "!", "audiorate", "!", "audioconvert", "!",
        "opusenc", "bitrate=96000", "bitrate-type=cbr", "frame-size=5",
        "bandwidth=fullband", "audio-type=restricted-lowdelay", "max-payload-size=1400",
        "!", "fakesink")
    forbidden = ("nvrtc", "nvidia", "nouveau", "radeonsi", "i965_drv_video")
    paths = [*Path("/opt/wolf-runtime").rglob("*"), *Path("/usr/local").rglob("*")]
    if any(any(word in p.name.lower() for word in forbidden) for p in paths):
        raise ValueError("unexpected multi-vendor payload")
    if any(Path("/usr/bin",tool).exists() for tool in ("gcc", "g++", "clang", "cargo", "cmake", "pebble")):
        raise ValueError("build tooling in runtime")
    print("Static libraries/plugins/license manifest checked; no GPU acceptance claimed.")


def health():
    # Presence of a supervisor process alone is not runtime readiness.
    workers = []
    for path in Path("/proc").glob("[0-9]*/comm"):
        try:
            if path.read_text().strip() == "wolf": workers.append(path)
        except (OSError, ProcessLookupError): pass
    if not workers: return False
    for port in (47984,47989,48010):
        try:
            with socket.create_connection(("127.0.0.1",port),timeout=0.5): pass
        except OSError: return False
    return True


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--static",action="store_true")
    parser.add_argument("--health",action="store_true")
    args=parser.parse_args()
    if args.static: static()
    elif args.health: sys.exit(0 if health() else 1)
    else: parser.error("select --static or --health")


if __name__ == "__main__": main()
