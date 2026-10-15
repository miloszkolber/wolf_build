"""Acquire lock-selected Git objects, including their exact submodules, for Docker."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))
from resolve import candidate_tag, fingerprint, is_full_sha, packaging_identity


def git(*args, cwd=None):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def validate_source(source):
    if not is_full_sha(source.get("sha")):
        raise ValueError("source requires a full Git commit")
    if not re.fullmatch(r"https://(?:github\.com|gitlab\.com)/[\w.-]+/[\w.-]+(?:\.git)?", source.get("url", "")):
        raise ValueError("source must use an approved HTTPS Git host")


def acquire(source, target):
    validate_source(source)
    if not (target / ".git").exists():
        target.mkdir(parents=True, exist_ok=True)
        git("init", str(target))
    if git("status", "--porcelain", "--untracked-files=all", "--ignore-submodules=all", cwd=target):
        raise ValueError("source cache contains unrecorded modifications: "+str(target))
    try:
        head = git("rev-parse", "HEAD", cwd=target)
    except subprocess.CalledProcessError:
        head = ""
    if head != source["sha"]:
        git("fetch", "--depth=1", source["url"], source["sha"], cwd=target)
        git("checkout", "--detach", source["sha"], cwd=target)
    if git("rev-parse", "HEAD", cwd=target) != source["sha"]:
        raise ValueError("Git object identity mismatch")
    git("submodule", "update", "--init", "--recursive", "--depth=1", cwd=target)
    submodules = git("submodule", "status", "--recursive", cwd=target)
    if any(line.startswith(("+", "-", "U")) for line in submodules.splitlines()):
        raise ValueError("submodule object identity mismatch")
    if git("status", "--porcelain", "--untracked-files=all", cwd=target):
        raise ValueError("submodule cache contains unrecorded modifications")
    return submodules


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=".build/manifest.json")
    parser.add_argument("--context", default=".build/context")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    if manifest.get("version") != 2 or not manifest["inputs"].get("sources"):
        raise ValueError("a version 2 --lock manifest is required")
    if manifest["inputs"].get("packaging") != packaging_identity(Path(__file__).resolve().parents[1]):
        raise ValueError("packaging changed after resolution; refresh the packaging identity or resolve a new lock")
    root = Path(args.context)
    cache = root.parent / "sources"
    root.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for name, source in manifest["inputs"]["sources"].items():
        if not re.fullmatch(r"[a-z0-9_-]+", name): raise ValueError("unsafe source name")
        print("Acquiring " + name, flush=True)
        cached = cache / name
        submodules = acquire(source, cached)
        inventory[name] = submodules
        destination = root / "sources" / name
        if destination.exists(): shutil.rmtree(destination)
        shutil.copytree(cached, destination, symlinks=True, ignore=shutil.ignore_patterns(".git"))
        licenses = root / "licenses" / name
        licenses.mkdir(parents=True, exist_ok=True)
        for path in cached.iterdir():
            if path.is_file() and re.match(r"(?i)(copying|copyright|licen[cs]e|notice)", path.name):
                shutil.copyfile(path, licenses / path.name)
        if not list(licenses.iterdir()):
            raise ValueError("no top-level license for " + name)
    manifest["inputs"]["submodules"] = inventory
    manifest["input_hash"] = fingerprint(manifest["inputs"])
    manifest["input_sha256"] = hashlib.sha256(json.dumps(manifest["inputs"],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    manifest["candidate_tag"] = candidate_tag(manifest["inputs"]["wolf"]["sha"], manifest["input_hash"])
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    cmake = "\n".join(f'set(FETCHCONTENT_SOURCE_DIR_{name} "/sources/{source}" CACHE PATH "Locked source" FORCE)' for name,source in manifest["inputs"]["cmake_sources"].items())
    (root / "locked-sources.cmake").write_text(cmake+"\n")
    base, rust = manifest["inputs"]["base"], manifest["inputs"]["toolchain"]
    snapshot=manifest["inputs"]["distribution_snapshot"]
    if not re.fullmatch(r"\d{8}T\d{6}Z",snapshot): raise ValueError("invalid distribution snapshot")
    # Only validated image/digest tokens are emitted as shell assignments.
    for item in (base,rust):
        if not re.fullmatch(r"[\w./:-]+",item["image"]) or not re.fullmatch(r"sha256:[a-f0-9]{64}",item["digest"]):
            raise ValueError("unlocked base/toolchain image")
    recipe=manifest["inputs"]["packaging"]["revision"]
    if not is_full_sha(recipe): raise ValueError("invalid packaging revision")
    (root.parent / "build.env").write_text(f'BASE_IMAGE={base["image"]}@{base["digest"]}\nRUST_IMAGE={rust["image"]}@{rust["digest"]}\nCANDIDATE_TAG={manifest["candidate_tag"]}\nINPUT_SHA256={manifest["input_sha256"]}\nRECIPE_REVISION={recipe}\nWOLF_SHA={manifest["inputs"]["wolf"]["sha"]}\nSECURITY_REFRESH={manifest["inputs"]["refresh_week"]}\nUBUNTU_SNAPSHOT={snapshot}\n')
    print("Acquired exact Git objects, not upstream-signed archive checksums.")


if __name__ == "__main__":
    main()
