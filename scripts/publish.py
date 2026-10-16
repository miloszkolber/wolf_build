"""Publish checked immutable images and advance the default channel to latest."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def command(*args):
    try:
        return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=1800).stdout.strip()
    except subprocess.CalledProcessError as error:
        print(error.stderr, file=sys.stderr)
        raise


def gh(path):
    return json.loads(command("gh", "api", path))


def image_name(name):
    if name not in ("wolf_runtime", "wolf_steam", "wolf_heroic"):
        raise ValueError("unknown image")
    owner = os.environ["GITHUB_REPOSITORY_OWNER"].lower()
    if not re.fullmatch(r"[a-z0-9-]+", owner):
        raise ValueError("invalid registry owner")
    return f"ghcr.io/{owner}/{name}"


def inspect(reference):
    try:
        result = command("docker", "buildx", "imagetools", "inspect", "--format",
                         '{"manifest":{{json .Manifest}},"image":{{json .Image}}}', reference)
    except subprocess.CalledProcessError as error:
        if re.search(r"manifest unknown|not found", error.stderr or "", re.I):
            return None
        raise
    result = json.loads(result)
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", result["manifest"]["digest"]):
        raise ValueError("registry returned an invalid digest")
    return result


def package_exists(name):
    repo = gh(f"repos/{os.environ['GITHUB_REPOSITORY']}")
    namespace = "orgs" if repo["owner"]["type"] == "Organization" else "users"
    owner = os.environ["GITHUB_REPOSITORY_OWNER"]
    try:
        gh(f"{namespace}/{owner}/packages/container/{name}")
    except subprocess.CalledProcessError as error:
        if "(HTTP 404)" in (error.stderr or ""):
            return False
        raise
    return True


def validate_tag(name, tag, identity):
    pattern = r"stable-[a-f0-9]{12}-[a-f0-9]{12}" if name == "wolf_runtime" else r"candidate-[a-f0-9]{16}"
    if not re.fullmatch(pattern, tag) or not re.fullmatch(r"[a-f0-9]{64}", identity):
        raise ValueError("invalid immutable tag/input identity")
    if not tag.endswith(identity[:12] if name == "wolf_runtime" else identity[:16]):
        raise ValueError("tag does not match the full input identity")


def validate_identity(labels, expected):
    if (labels or {}).get("io.wolf-build.input-sha256") != expected:
        raise ValueError("immutable image identity collision")


def existing(name, tag, identity):
    reference = f"{image_name(name)}:{tag}"
    # An empty GHCR namespace can deny pull scope. Confirm its absence through
    # authenticated package metadata, never by ignoring arbitrary Docker errors.
    if not package_exists(name):
        return None
    result = inspect(reference)
    if result:
        validate_identity(result["image"]["config"].get("Labels", {}), identity)
    return result


def reuse(name, tag, identity, local):
    result = existing(name, tag, identity)
    if result:
        reference = f"{image_name(name)}@{result['manifest']['digest']}"
        command("docker", "pull", reference)
        command("docker", "tag", reference, local)
    return bool(result)


def newer_publication_exists(name):
    """Do not let an old workflow re-run roll latest back after a newer writer."""
    repo = os.environ["GITHUB_REPOSITORY"]
    number = int(os.environ["GITHUB_RUN_NUMBER"])
    workflow = Path(os.environ["GITHUB_WORKFLOW_REF"].split("@", 1)[0]).name
    if workflow not in ("build.yml", "apps.yml") or number < 1:
        raise ValueError("latest requires a build-workflow run identity")
    job_name = "publish" if name == "wolf_runtime" else f"publish ({name.removeprefix('wolf_')})"
    for page in range(1, 21):
        runs = gh(f"repos/{repo}/actions/workflows/{workflow}/runs?branch=main&per_page=100&page={page}")["workflow_runs"]
        newer = [run for run in runs if run["run_number"] > number and run["event"] != "pull_request"]
        for run in newer:
            jobs = gh(f"repos/{repo}/actions/runs/{run['id']}/jobs?filter=all&per_page=100")["jobs"]
            if any(job["name"] == job_name and any(
                step["name"] == "Publish checked image and latest" and step["conclusion"] == "success"
                for step in job.get("steps", [])
            ) for job in jobs):
                return True
        if not runs or any(run["run_number"] <= number for run in runs):
            return False
    raise ValueError("cannot establish publication order for this old run; latest unchanged")


def publish(name, tag, identity, local, latest=True):
    labels = json.loads(command("docker", "image", "inspect", local, "--format", "{{json .Config.Labels}}"))
    validate_identity(labels, identity)
    image = image_name(name)
    result = existing(name, tag, identity)
    if result is None:
        command("docker", "tag", local, f"{image}:{tag}")
        print(command("docker", "push", f"{image}:{tag}"), flush=True)
        result = inspect(f"{image}:{tag}")
        if result is None:
            raise ValueError("published immutable tag is missing")
        validate_identity(result["image"]["config"].get("Labels", {}), identity)
    digest = result["manifest"]["digest"]
    outcome = "candidate-only"
    if latest:
        if newer_publication_exists(name):
            outcome = "newer successful publication retained"
        else:
            # The checked immutable tag is already the staging/rollback reference.
            command("docker", "buildx", "imagetools", "create", "--prefer-index=false",
                    "--tag", f"{image}:latest", f"{image}@{digest}")
            current = inspect(f"{image}:latest")
            if current is None or current["manifest"]["digest"] != digest:
                raise ValueError("latest digest does not match checked immutable image")
            outcome = "latest"
    summary = f"{image}:{tag} @ {digest} — {outcome}"
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
            output.write(summary + "\n")
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "publish"))
    parser.add_argument("image", choices=("wolf_runtime", "wolf_steam", "wolf_heroic"))
    parser.add_argument("tag")
    parser.add_argument("identity")
    parser.add_argument("local")
    parser.add_argument("--candidate-only", action="store_true")
    args = parser.parse_args()
    validate_tag(args.image, args.tag, args.identity)
    if args.action == "check":
        unchanged = reuse(args.image, args.tag, args.identity, args.local)
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write(f"unchanged={str(unchanged).lower()}\n")
    else:
        if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
            raise ValueError("only trusted default-branch builds may publish")
        publish(args.image, args.tag, args.identity, args.local, latest=not args.candidate_only)


if __name__ == "__main__":
    main()
