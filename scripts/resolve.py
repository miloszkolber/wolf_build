"""Resolve exact upstream inputs for the Intel Wolf runtime and write a manifest."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MANIFEST_VERSION = 1
WOLF_REPO = "games-on-whales/wolf"
WOLF_REF = "stable"
COMPOSITOR_REPO = "games-on-whales/gst-wayland-display"
COMPOSITOR_PIN = "016b4fc"
INTERPIPE_REPO = "games-on-whales/gst-interpipe"
GSTREAMER_DEFAULT = "1.26.7"
GSTREAMER_SERIES = "1.26"
INTEL_MEDIA_REPO = "intel/media-driver"
INTEL_VPL_REPO = "intel/vpl-gpu-rt"
INTEL_LIBVPL_REPO = "intel/libvpl"
BASE_IMAGE = "ubuntu:26.04"
GATE_IMAGE = "ghcr.io/miloszkolber/gate"


def is_full_sha(value):
    return bool(re.fullmatch(r"[0-9a-f]{40}", value or ""))


def check_gstreamer(version):
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version or "")
    if not match:
        raise ValueError("gstreamer version must look like 1.26.7, not a branch")
    series = match.group(1) + "." + match.group(2)
    if series != GSTREAMER_SERIES:
        raise ValueError("gstreamer series " + series + " is outside the accepted " + GSTREAMER_SERIES + " series")
    return version


def intel_core_version(media_tag, vpl_tag):
    media = re.fullmatch(r"intel-media-(\d+\.\d+\.\d+)", media_tag or "")
    vpl = re.fullmatch(r"intel-onevpl-(\d+\.\d+\.\d+)", vpl_tag or "")
    if not media or not vpl:
        raise ValueError("intel tags must look like intel-media-26.3.5 and intel-onevpl-26.3.5")
    if media.group(1) != vpl.group(1):
        raise ValueError("intel media-driver and vpl-gpu-rt core versions differ")
    return media.group(1)


def select_wolf(explicit, stable_sha):
    if explicit:
        if not is_full_sha(explicit):
            raise ValueError("wolf override must be a full source commit, not a branch")
        return explicit
    if not is_full_sha(stable_sha):
        raise ValueError("wolf stable HEAD did not resolve to a full commit")
    return stable_sha


def select_named_sha(name, explicit, discovered):
    if explicit:
        if not is_full_sha(explicit):
            raise ValueError(name + " override must be a full source commit")
        return explicit
    if not is_full_sha(discovered):
        raise ValueError(name + " HEAD did not resolve to a full commit")
    return discovered


def candidate_tag(wolf_sha, fingerprint):
    if not is_full_sha(wolf_sha) or not re.fullmatch(r"[0-9a-f]{12}", fingerprint or ""):
        raise ValueError("candidate tag needs a full wolf SHA and a 12-character input hash")
    return "stable-" + wolf_sha[:12] + "-" + fingerprint


def fingerprint(inputs):
    canonical = json.dumps(inputs, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


def build_manifest(wolf_sha, gstreamer_version, compositor_sha, interpipe_sha, media_tag, vpl_tag, libvpl_tag, base_digest, gate_tag="", gate_digest=""):
    check_gstreamer(gstreamer_version)
    wolf_sha = select_wolf("", wolf_sha)
    compositor_sha = select_named_sha("compositor", "", compositor_sha)
    interpipe_sha = select_named_sha("interpipe", "", interpipe_sha)
    core = intel_core_version(media_tag, vpl_tag)
    if not re.fullmatch(r"v\d+\.\d+\.\d+", libvpl_tag or ""):
        raise ValueError("libvpl tag must look like v2.17.0")
    if base_digest and not re.fullmatch(r"sha256:[0-9a-f]{64}", base_digest):
        raise ValueError("base digest must look like sha256:<64 hex>")
    if (gate_tag or gate_digest) and not (gate_tag and re.fullmatch(r"sha256:[0-9a-f]{64}", gate_digest or "")):
        raise ValueError("gate needs both a tag and a full digest, or neither while publication is pending")
    inputs = {
        "wolf": {"repo": WOLF_REPO, "ref": WOLF_REF, "sha": wolf_sha},
        "gstreamer": {"version": gstreamer_version, "series": GSTREAMER_SERIES},
        "compositor": {"repo": COMPOSITOR_REPO, "sha": compositor_sha},
        "interpipe": {"repo": INTERPIPE_REPO, "sha": interpipe_sha},
        "intel": {"media_driver": media_tag, "vpl_gpu_rt": vpl_tag, "libvpl": libvpl_tag, "core_version": core},
        "base": {"image": BASE_IMAGE, "digest": base_digest or ""},
        "gate": {"image": GATE_IMAGE, "tag": gate_tag or "", "digest": gate_digest or "", "status": "resolved" if gate_tag else "pending-publication"},
    }
    short = wolf_sha[:12]
    tag = candidate_tag(wolf_sha, fingerprint(inputs))
    return {
        "version": MANIFEST_VERSION,
        "generated": datetime.now(timezone.utc).date().isoformat(),
        "wolf_short": short,
        "candidate_tag": tag,
        "input_hash": fingerprint(inputs),
        "inputs": inputs,
    }


def github_api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "wolf_build"}
    if os.getenv("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    for attempt in range(3):
        try:
            with urlopen(Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as err:
            if err.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
            time.sleep(2 ** attempt)


def git_ls_remote(url, *refs):
    out = subprocess.check_output(["git", "ls-remote", url, *refs], text=True)
    values = dict(line.split()[::-1] for line in out.splitlines() if line.strip())
    return values


def discover_wolf_stable():
    values = git_ls_remote("https://github.com/" + WOLF_REPO + ".git", "refs/heads/" + WOLF_REF)
    sha = values.get("refs/heads/" + WOLF_REF, "")
    return select_wolf("", sha)


def discover_component_master(repo):
    values = git_ls_remote("https://github.com/" + repo + ".git", "refs/heads/master")
    sha = values.get("refs/heads/master", "")
    return select_named_sha(repo, "", sha)


def discover_compositor_pin():
    commit = github_api("repos/" + COMPOSITOR_REPO + "/commits/" + COMPOSITOR_PIN)
    sha = commit.get("sha", "")
    if not is_full_sha(sha):
        raise ValueError("compositor pin did not resolve to a full commit")
    return sha


def discover_gstreamer(version):
    req = Request(
        "https://gitlab.freedesktop.org/api/v4/projects/gstreamer%2Fgstreamer/repository/tags/" + version,
        headers={"User-Agent": "wolf_build"},
    )
    for attempt in range(3):
        try:
            with urlopen(req, timeout=30) as response:
                tag = json.load(response)
                break
        except HTTPError as err:
            if err.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise ValueError("gstreamer version not found: " + version)
            time.sleep(2 ** attempt)
    if tag.get("name") != version:
        raise ValueError("gstreamer version not found: " + version)
    return check_gstreamer(version)


def discover_intel():
    media = github_api("repos/" + INTEL_MEDIA_REPO + "/releases/latest")
    vpl = github_api("repos/" + INTEL_VPL_REPO + "/releases/latest")
    libvpl = github_api("repos/" + INTEL_LIBVPL_REPO + "/releases/latest")
    if media.get("draft") or media.get("prerelease") or vpl.get("draft") or vpl.get("prerelease"):
        raise ValueError("intel media stack latest must be a stable release")
    core = intel_core_version(media.get("tag_name", ""), vpl.get("tag_name", ""))
    return {"media": media["tag_name"], "vpl": vpl["tag_name"], "libvpl": libvpl["tag_name"], "core": core}


def discover_base_digest():
    req = Request("https://hub.docker.com/v2/repositories/library/ubuntu/tags/26.04", headers={"User-Agent": "wolf_build"})
    for attempt in range(3):
        try:
            with urlopen(req, timeout=30) as response:
                payload = json.load(response)
                break
        except HTTPError as err:
            if err.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
            time.sleep(2 ** attempt)
    for image in payload.get("images", []):
        if image.get("architecture") == "amd64" and image.get("os") == "linux":
            digest = image.get("digest", "")
            if re.fullmatch(r"sha256:[0-9a-f]{64}", digest or ""):
                return digest
    raise ValueError("ubuntu:26.04 has no amd64 linux digest")


def emit(values):
    for key, value in values.items():
        print(key + "=" + value)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            for key, value in values.items():
                output.write(key + "=" + value + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wolf-sha", default="")
    parser.add_argument("--gstreamer-version", default=GSTREAMER_DEFAULT)
    parser.add_argument("--compositor-sha", default="")
    parser.add_argument("--interpipe-sha", default="")
    parser.add_argument("--media-driver-tag", default="")
    parser.add_argument("--vpl-tag", default="")
    parser.add_argument("--libvpl-tag", default="")
    parser.add_argument("--base-digest", default="")
    parser.add_argument("--gate-tag", default="")
    parser.add_argument("--gate-digest", default="")
    parser.add_argument("--output", default=".build/manifest.json")
    args = parser.parse_args()
    wolf_sha = args.wolf_sha or discover_wolf_stable()
    gstreamer_version = discover_gstreamer(args.gstreamer_version)
    compositor_sha = args.compositor_sha or discover_compositor_pin()
    interpipe_sha = args.interpipe_sha or discover_component_master(INTERPIPE_REPO)
    if args.media_driver_tag or args.vpl_tag or args.libvpl_tag:
        if not (args.media_driver_tag and args.vpl_tag and args.libvpl_tag):
            raise ValueError("intel overrides need media-driver, vpl-gpu-rt and libvpl tags together")
        intel = {"media": args.media_driver_tag, "vpl": args.vpl_tag, "libvpl": args.libvpl_tag, "core": intel_core_version(args.media_driver_tag, args.vpl_tag)}
    else:
        intel = discover_intel()
    base_digest = args.base_digest or discover_base_digest()
    manifest = build_manifest(wolf_sha, gstreamer_version, compositor_sha, interpipe_sha, intel["media"], intel["vpl"], intel["libvpl"], base_digest, args.gate_tag, args.gate_digest)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    emit({"tag": manifest["candidate_tag"], "sha": wolf_sha, "input_hash": manifest["input_hash"], "manifest": str(path)})


if __name__ == "__main__":
    main()
