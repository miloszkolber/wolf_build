"""Turn APT's exact selected closure into build locks and image input identity."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def package_key(name, arch):
    name = name.split(":", 1)[0]
    if not re.fullmatch(r"[a-z0-9][a-z0-9+.-]*", name) or arch not in ("amd64", "i386", "all"):
        raise ValueError("invalid package/architecture")
    return name if arch == "all" else name + ":" + arch


def version(value):
    if not re.fullmatch(r"[0-9][a-zA-Z0-9.+:~_-]*", value):
        raise ValueError("invalid package version")
    return value


def parse_plan(text, stages):
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("@@"):
            current = line[2:]
            if current in sections or current not in ("installed", *stages):
                raise ValueError("unexpected or repeated package plan section")
            sections[current] = []
        elif current is None:
            raise ValueError("unframed package plan output")
        else:
            sections[current].append(line)
    if set(sections) != {"installed", *stages}:
        raise ValueError("incomplete package plan")
    installed = {}
    for line in sections["installed"]:
        name, arch, selected = line.split("\t")
        key = package_key(name, arch)
        if key in installed:
            raise ValueError("duplicate installed package")
        installed[key] = version(selected)
    if not installed:
        raise ValueError("empty base package inventory")
    closures = {}
    for stage in stages:
        selected = dict(installed)
        for line in sections[stage]:
            if line.startswith("Remv "):
                raise ValueError("package solver unexpectedly removes a base package")
            if not line.startswith("Inst "):
                continue
            match = re.fullmatch(r"Inst (\S+)(?: \[[^]]+\])? \((\S+) .*\[(amd64|i386|all)\]\)(?: \[[^]]*\])*", line)
            if not match:
                raise ValueError("unrecognized APT selection: " + line)
            name, selected_version, arch = match.groups()
            selected[package_key(name, arch)] = version(selected_version)
        closures[stage] = dict(sorted(selected.items()))
    return closures


def apply(manifest, profile, closures):
    inputs = manifest["inputs"]
    inputs["distribution"] = closures
    digest = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    manifest["input_sha256"] = digest
    if profile == "runtime":
        manifest["input_hash"] = digest[:12]
        manifest["candidate_tag"] = "stable-" + inputs["wolf"]["sha"][:12] + "-" + digest[:12]
    else:
        manifest["tag"] = "candidate-" + digest[:16]
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=("runtime", "steam", "heroic"))
    args = parser.parse_args()
    profile = args.profile
    manifest_path = Path(".build/manifest.json" if profile == "runtime" else ".build/context/apps/manifest.json")
    manifest = json.loads(manifest_path.read_text())
    if profile != "runtime" and manifest["inputs"]["app"] != profile:
        raise ValueError("manifest belongs to a different app")
    stages = ("build", "runtime") if profile == "runtime" else ("common", profile)
    output = Path(".build/context/packages")
    closures = parse_plan((output / f"{profile}.plan").read_text(), stages)
    for stage, packages in closures.items():
        (output / f"{stage}.lock").write_text("".join(f"{name}={selected}\n" for name, selected in packages.items()))
    manifest = apply(manifest, profile, closures)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
