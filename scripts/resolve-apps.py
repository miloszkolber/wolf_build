"""Resolve the application base and Heroic release before Docker assembly."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from resolve import BASE_IMAGE, discover_base_digest, github_api


def heroic_asset(release):
    tag = release.get("tag_name", "")
    import re
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("Heroic must be a stable release")
    name = f"Heroic-{tag[1:]}-linux-amd64.deb"
    assets = [a for a in release["assets"] if a["name"] == name]
    if len(assets) != 1:
        raise ValueError("missing unambiguous Heroic deb")
    asset = assets[0]
    url = f"https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/{tag}/{name}"
    if asset["browser_download_url"] != url or not re.fullmatch(r"sha256:[a-f0-9]{64}", asset.get("digest", "")):
        raise ValueError("Heroic asset lacks a verified release identity")
    return {"version": tag[1:], "url": url, "sha256": asset["digest"][7:]}


def recipe_hash(root, app):
    digest = hashlib.sha256()
    paths = [root / ".dockerignore", root / "docker/apps.Dockerfile", root / "scripts/resolve-apps.py", root / "scripts/resolve.py",
             *(root / "scripts" / name for name in ("package-plan.sh", "resolve-packages.sh", "lock-packages.py", "install-packages.sh")),
             root / "docker/packages/common.txt", root / f"docker/packages/{app}.txt",
             *sorted((root / "docker/apps").glob("*"))]
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
            raise ValueError("Heroic asset checksum mismatch")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True, choices=("steam", "heroic"))
    parser.add_argument("--output", type=Path, default=Path(".build/context/apps"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    inputs = {
        "app": args.app,
        "base": BASE_IMAGE + "@" + discover_base_digest(),
        "recipe_sha256": recipe_hash(root, args.app),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    if args.app == "heroic":
        inputs["heroic"] = heroic_asset(github_api("repos/Heroic-Games-Launcher/HeroicGamesLauncher/releases/latest"))
        download(inputs["heroic"], args.output / "heroic.deb")
        (args.output / "heroic.sha256").write_text(inputs["heroic"]["sha256"] + "  heroic.deb\n")
    else:
        inputs["steam"] = "Ubuntu steam-installer; Valve client updates per-user at launch"
    # This discovery record cannot publish until lock-packages adds the closure.
    manifest = {"version": 2, "generated": datetime.now(timezone.utc).isoformat(), "inputs": inputs}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
