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
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MANIFEST_VERSION = 1
WOLF_REPO = "games-on-whales/wolf"
WOLF_REF = "stable"
# Upstream moved `stable` to its latest published GitHub release during the
# 2026-10 release-channel migration. The only published release is v2024.07
# (40b0c5c, 2024-07-10), which predates the build metadata this lock reads and
# cannot be built here, so discovery holds the last reviewed source commit until
# upstream publishes its first calendar release. Review and clear the hold then;
# openspec/maintenance-state.md records the reviewed identity.
WOLF_SHA_PIN = "6a5053b4ebbb19f2c0f3bf1e8fbbd8babf109273"
COMPOSITOR_REPO = "games-on-whales/gst-wayland-display"
COMPOSITOR_PIN = "016b4fc"
INTERPIPE_REPO = "games-on-whales/gst-interpipe"
GSTREAMER_DEFAULT = "1.26.7"
GSTREAMER_SERIES = "1.26"
INTEL_MEDIA_REPO = "intel/media-driver"
INTEL_VPL_REPO = "intel/vpl-gpu-rt"
INTEL_LIBVPL_REPO = "intel/libvpl"
BASE_IMAGE = "ubuntu:26.04"


def is_full_sha(value):
    return bool(re.fullmatch(r"[0-9a-f]{40}", value or ""))


def check_gstreamer(version, accepted_series=GSTREAMER_SERIES):
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version or "")
    if not match:
        raise ValueError("gstreamer version must look like 1.26.7, not a branch")
    series = match.group(1) + "." + match.group(2)
    if series != accepted_series:
        raise ValueError("gstreamer series " + series + " is outside the accepted " + accepted_series + " series")
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


def build_manifest(wolf_sha, gstreamer_version, compositor_sha, interpipe_sha, media_tag, vpl_tag, libvpl_tag, base_digest, gstreamer_series=GSTREAMER_SERIES):
    check_gstreamer(gstreamer_version,gstreamer_series)
    wolf_sha = select_wolf("", wolf_sha)
    compositor_sha = select_named_sha("compositor", "", compositor_sha)
    interpipe_sha = select_named_sha("interpipe", "", interpipe_sha)
    core = intel_core_version(media_tag, vpl_tag)
    if not re.fullmatch(r"v\d+\.\d+\.\d+", libvpl_tag or ""):
        raise ValueError("libvpl tag must look like v2.17.0")
    if base_digest and not re.fullmatch(r"sha256:[0-9a-f]{64}", base_digest):
        raise ValueError("base digest must look like sha256:<64 hex>")
    inputs = {
        "wolf": {"repo": WOLF_REPO, "ref": WOLF_REF, "sha": wolf_sha},
        "gstreamer": {"version": gstreamer_version, "series": gstreamer_series},
        "compositor": {"repo": COMPOSITOR_REPO, "sha": compositor_sha},
        "interpipe": {"repo": INTERPIPE_REPO, "sha": interpipe_sha},
        "intel": {"media_driver": media_tag, "vpl_gpu_rt": vpl_tag, "libvpl": libvpl_tag, "core_version": core},
        "base": {"image": BASE_IMAGE, "digest": base_digest or ""},
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
    """Resolve Wolf's source from its release channel, or the reviewed pin."""
    if WOLF_SHA_PIN:
        if not is_full_sha(WOLF_SHA_PIN):
            raise ValueError("wolf source pin must be a full source commit")
        return WOLF_SHA_PIN
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


def discover_gstreamer(version, accepted_series=GSTREAMER_SERIES):
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
    return check_gstreamer(version,accepted_series)


def discover_gstreamer_patch(series=GSTREAMER_SERIES):
    request=Request("https://gitlab.freedesktop.org/api/v4/projects/gstreamer%2Fgstreamer/repository/tags?search=%5E"+series+".&per_page=100",headers={"User-Agent":"wolf_build"})
    with urlopen(request,timeout=30) as response:
        tags=json.load(response)
    eligible=[entry["name"] for entry in tags if re.fullmatch(re.escape(series)+r"\.\d+",entry.get("name",""))]
    if not eligible: raise ValueError("no stable patch release in compatible GStreamer series")
    return max(eligible,key=lambda tag:tuple(map(int,tag.split("."))))


def discover_intel():
    media = github_api("repos/" + INTEL_MEDIA_REPO + "/releases/latest")
    vpl = github_api("repos/" + INTEL_VPL_REPO + "/releases/latest")
    libvpl = github_api("repos/" + INTEL_LIBVPL_REPO + "/releases/latest")
    if any(item.get("draft") or item.get("prerelease") for item in (media, vpl, libvpl)):
        raise ValueError("intel media stack latest must be a stable release")
    core = intel_core_version(media.get("tag_name", ""), vpl.get("tag_name", ""))
    return {"media": media["tag_name"], "vpl": vpl["tag_name"], "libvpl": libvpl["tag_name"], "core": core}


def discover_base_digest():
    return hub_digest("ubuntu", "26.04")


def hub_digest(image, tag):
    req = Request(f"https://hub.docker.com/v2/repositories/library/{image}/tags/{tag}", headers={"User-Agent": "wolf_build"})
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
    raise ValueError(f"{image}:{tag} has no amd64 linux digest")


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
    parser.add_argument("--gstreamer-version", default="")
    parser.add_argument("--compositor-sha", default="")
    parser.add_argument("--interpipe-sha", default="")
    parser.add_argument("--media-driver-tag", default="")
    parser.add_argument("--vpl-tag", default="")
    parser.add_argument("--libvpl-tag", default="")
    parser.add_argument("--base-digest", default="")
    parser.add_argument("--output", default=".build/manifest.json")
    parser.add_argument("--lock", action="store_true", help="Resolve all build sources, base and toolchain into a buildable lock")
    args = parser.parse_args()
    wolf_sha = args.wolf_sha or discover_wolf_stable()
    series=GSTREAMER_SERIES
    if args.lock:
        declared=re.search(r"ARG GSTREAMER_VERSION=([\d.]+)",raw(WOLF_REPO,wolf_sha,"docker/gstreamer.Dockerfile"))
        if not declared: raise ValueError("Wolf does not declare its GStreamer version")
        series=declared.group(1).rsplit(".",1)[0]
    gstreamer_version = discover_gstreamer(args.gstreamer_version or discover_gstreamer_patch(series),series)
    if args.compositor_sha:
        compositor_sha = args.compositor_sha
    elif args.lock:
        declaration=raw(WOLF_REPO,wolf_sha,"docker/wolf.Dockerfile")
        pin=re.search(r"git checkout ([a-f0-9]{7,40})",declaration)
        if not pin: raise ValueError("Wolf does not declare a compatible compositor pin")
        compositor_sha=source_commit("https://github.com/"+COMPOSITOR_REPO+".git",pin.group(1))
    else:
        compositor_sha = discover_compositor_pin()
    interpipe_sha = args.interpipe_sha or discover_component_master(INTERPIPE_REPO)
    if args.media_driver_tag or args.vpl_tag or args.libvpl_tag:
        if not (args.media_driver_tag and args.vpl_tag and args.libvpl_tag):
            raise ValueError("intel overrides need media-driver, vpl-gpu-rt and libvpl tags together")
        intel = {"media": args.media_driver_tag, "vpl": args.vpl_tag, "libvpl": args.libvpl_tag, "core": intel_core_version(args.media_driver_tag, args.vpl_tag)}
    else:
        intel = discover_intel()
    base_digest = args.base_digest or discover_base_digest()
    manifest = build_manifest(wolf_sha, gstreamer_version, compositor_sha, interpipe_sha, intel["media"], intel["vpl"], intel["libvpl"], base_digest,gstreamer_series=series)
    if args.lock:
        manifest = lock_sources(manifest, compositor_override=args.compositor_sha)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    emit({"tag": manifest["candidate_tag"], "sha": wolf_sha, "input_hash": manifest["input_hash"], "manifest": str(path)})


def source_commit(url, ref):
    if is_full_sha(ref):
        return ref
    match = re.fullmatch(r"https://github.com/([\w.-]+/[\w.-]+?)(?:\.git)?", url)
    if match:
        sha = github_api("repos/" + match[1] + "/commits/" + quote(ref, safe=""))["sha"]
    elif url == "https://gitlab.com/ReenigneArcher/Simple-Web-Server.git":
        request = Request("https://gitlab.com/api/v4/projects/ReenigneArcher%2FSimple-Web-Server/repository/commits/" + quote(ref, safe=""), headers={"User-Agent":"wolf_build"})
        with urlopen(request, timeout=30) as response:
            sha = json.load(response)["id"]
    else:
        raise ValueError("unrecognized source URL: " + url)
    if not is_full_sha(sha):
        raise ValueError("source ref did not resolve to full commit: " + url)
    return sha


def raw(repo, sha, path):
    with urlopen(Request(f"https://raw.githubusercontent.com/{repo}/{sha}/{path}", headers={"User-Agent":"wolf_build"}), timeout=30) as response:
        return response.read().decode()


def lock_sources(manifest, compositor_override=""):
    """Expand release names into exact sources and Wolf's declared CMake inputs."""
    inputs = manifest["inputs"]
    sources = {}
    def add(name, url, ref):
        entry = {"url":url, "ref":ref, "sha":source_commit(url, ref)}
        if name in sources and sources[name] != entry:
            raise ValueError("conflicting source declarations for " + name)
        sources[name] = entry
    wolf_sha = inputs["wolf"]["sha"]
    add("wolf", "https://github.com/games-on-whales/wolf.git", wolf_sha)
    dockerfile = raw(WOLF_REPO, wolf_sha, "docker/wolf.Dockerfile")
    gstfile = raw(WOLF_REPO, wolf_sha, "docker/gstreamer.Dockerfile")
    gst = re.search(r"ARG GSTREAMER_VERSION=([\d.]+)", gstfile)
    pin = re.search(r"git checkout ([a-f0-9]{7,40})", dockerfile)
    rust = re.search(r"ARG RUST_VERSION=([\d.]+)", dockerfile)
    if not all((gst, pin, rust)):
        raise ValueError("Wolf build metadata changed; review compatibility before building")
    if inputs["gstreamer"]["version"].rsplit(".",1)[0] != gst.group(1).rsplit(".",1)[0]:
        raise ValueError("GStreamer series differs from Wolf's declaration")
    add("gstreamer", "https://github.com/GStreamer/gstreamer.git", inputs["gstreamer"]["version"])
    add("compositor", "https://github.com/"+COMPOSITOR_REPO+".git", compositor_override or pin.group(1))
    inputs["compositor"] = {"repo":COMPOSITOR_REPO, "sha":sources["compositor"]["sha"]}
    add("interpipe", "https://github.com/"+INTERPIPE_REPO+".git", inputs["interpipe"]["sha"])
    release = github_api("repos/"+INTEL_VPL_REPO+"/releases/tags/"+inputs["intel"]["vpl_gpu_rt"])
    body = release.get("body", "")
    dependencies = {
        "gmmlib": ("intel/gmmlib", r"intel-gmmlib-\d+\.\d+\.\d+"),
        "libva": ("intel/libva", r"intel/libva/releases/tag/([\d.]+)"),
        "libvpl": ("intel/libvpl", r"intel/libvpl/releases/tag/(v[\d.]+)"),
    }
    for name, (repo, pattern) in dependencies.items():
        found = re.search(pattern, body)
        if not found: raise ValueError("Intel runtime release does not identify " + name)
        ref = found.group(1) if found.lastindex else found.group(0)
        if name == "libvpl" and ref != inputs["intel"]["libvpl"]:
            raise ValueError("dispatcher differs from Intel's declared stack")
        add(name, "https://github.com/"+repo+".git", ref)
    add("media-driver", "https://github.com/"+INTEL_MEDIA_REPO+".git", inputs["intel"]["media_driver"])
    add("vpl-gpu-rt", "https://github.com/"+INTEL_VPL_REPO+".git", inputs["intel"]["vpl_gpu_rt"])
    tree = github_api(f"repos/{WOLF_REPO}/git/trees/{wolf_sha}?recursive=1")
    if tree.get("truncated"): raise ValueError("truncated Wolf source tree")
    cmake = {}
    for entry in tree["tree"]:
        path = entry["path"]
        if path.startswith("tests/") or not (path.endswith("CMakeLists.txt") or path.endswith(".cmake")): continue
        text = raw(WOLF_REPO, wolf_sha, path)
        for block in re.finditer(r"FetchContent_Declare\(\s*([\w-]+)(.*?)\)\s*", text, re.S):
            name, content = block.groups()
            repo = re.search(r"GIT_REPOSITORY\s+([^\s)]+)", content)
            ref = re.search(r"GIT_TAG\s+([^\s)]+)", content)
            if not repo: continue  # Boost uses distribution packages, not its URL fallback.
            key = "wolf-"+name.lower()
            add(key, repo.group(1), ref.group(1) if ref else "HEAD")
            cmake[name.upper()] = key
    inputs["sources"] = sources
    inputs["cmake_sources"] = cmake
    # Toolchain discovery is separate from the runtime payload.
    rust_tag = rust.group(1)+"-slim-bookworm"
    inputs["toolchain"] = {"rust_version":rust.group(1), "image":f"rust:{rust_tag}", "digest":hub_digest("rust", rust_tag)}
    inputs["packaging"] = packaging_identity(Path(__file__).resolve().parents[1])
    manifest["input_hash"] = fingerprint(inputs)
    manifest["candidate_tag"] = candidate_tag(wolf_sha, manifest["input_hash"])
    manifest["version"] = 2
    return manifest


# Files owned by the runtime candidate identity. Application packaging
# (apps Dockerfile, its scripts and docs tooling) must not force runtime
# rebuilds; application sources have their own recipe hash in resolve-apps.py.
RUNTIME_PACKAGING = (
    ".dockerignore",
    "docker/wolf.Dockerfile",
    "scripts/build-inputs.py",
    "scripts/build.sh",
    "scripts/check-runtime.py",
    "scripts/collect-rust-licenses.py",
    "scripts/compile-compositor.sh",
    "scripts/compile-gstreamer.sh",
    "scripts/compile-runtime.sh",
    "scripts/compile-wolf.sh",
    "scripts/resolve.py",
    "scripts/package-plan.sh",
    "scripts/resolve-packages.sh",
    "scripts/lock-packages.py",
    "scripts/install-packages.sh",
    "docker/packages/build.txt",
    "docker/packages/runtime.txt",
)


def packaging_identity(root):
    if subprocess.check_output(["git", "rev-parse", "--is-shallow-repository"], cwd=root, text=True).strip() == "true":
        raise ValueError("runtime provenance requires full Git history (checkout fetch-depth: 0)")
    packaging = hashlib.sha256()
    for name in RUNTIME_PACKAGING:
        path = root / name
        packaging.update(name.encode()+b"\0"+path.read_bytes())
    revision=subprocess.check_output(["git","log","-1","--format=%H","--",*RUNTIME_PACKAGING],cwd=root,text=True).strip()
    dirty=bool(subprocess.check_output(["git","status","--porcelain","--",*RUNTIME_PACKAGING],cwd=root,text=True).strip())
    return {"sha256":packaging.hexdigest(), "revision":revision, "dirty":dirty}


if __name__ == "__main__":
    main()
