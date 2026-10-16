"""Resolve the application base and Lutris release before Docker assembly."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from resolve import BASE_IMAGE, discover_base_digest, github_api


def lutris_asset(release):
    tag = release.get("tag_name", "")
    import re
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("Lutris must be a stable release")
    name = f"lutris_{tag[1:]}_all.deb"
    assets = [a for a in release["assets"] if a["name"] == name]
    if len(assets) != 1:
        raise ValueError("missing unambiguous Lutris deb")
    asset = assets[0]
    url = f"https://github.com/lutris/lutris/releases/download/{tag}/{name}"
    if asset["browser_download_url"] != url or not re.fullmatch(r"sha256:[a-f0-9]{64}", asset.get("digest", "")):
        raise ValueError("Lutris asset lacks a verified release identity")
    return {"version": tag[1:], "url": url, "sha256": asset["digest"][7:]}


def recipe_hash(root):
    digest = hashlib.sha256()
    paths = [root / ".dockerignore", root / "docker/apps.Dockerfile", root / "scripts/resolve-apps.py", root / "scripts/resolve.py", *sorted((root / "docker/apps").glob("*"))]
    for path in paths:
        digest.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def identity(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def download(asset, target):
    temporary = target.with_suffix(".partial")
    try:
        with urlopen(Request(asset["url"], headers={"User-Agent": "wolf-build"}), timeout=120) as response, temporary.open("wb") as output:
            digest = hashlib.sha256()
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != asset["sha256"]:
            raise ValueError("Lutris asset checksum mismatch")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".build/context/apps"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    inputs = {
        "base": BASE_IMAGE + "@" + discover_base_digest(),
        "lutris": lutris_asset(github_api("repos/lutris/lutris/releases/latest")),
        "refresh": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "recipe_sha256": recipe_hash(root),
        "steam": "Ubuntu steam-installer; Valve client updates per-user at launch",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    download(inputs["lutris"], args.output / "lutris.deb")
    (args.output / "lutris.sha256").write_text(inputs["lutris"]["sha256"] + "  lutris.deb\n")
    digest = identity(inputs)
    manifest = {"version": 1, "inputs": inputs, "input_sha256": digest, "tag": "candidate-" + digest[:16]}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
