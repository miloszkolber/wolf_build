"""Shared upstream metadata discovery for runtime and application images."""
import json
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_IMAGE = "ubuntu:26.04"


def fetch(request, timeout=30, *, opener=None, sleep=None):
    """Bound and retry small upstream metadata reads, never missing artifacts."""
    opener = opener or urlopen
    sleep = sleep or time.sleep
    for attempt in range(3):
        try:
            with opener(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as err:
            if err.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
        except (URLError, TimeoutError, ConnectionError):
            if attempt == 2:
                raise
        sleep(2 ** attempt)


def github_api(path, *, read=fetch):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "wolf_build"}
    if os.getenv("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    return json.loads(read(Request("https://api.github.com/" + path, headers=headers)))


def discover_base_digest(*, lookup=None):
    return (lookup or hub_digest)("ubuntu", "26.04")


def hub_digest(image, tag, *, read=fetch):
    req = Request(f"https://hub.docker.com/v2/repositories/library/{image}/tags/{tag}", headers={"User-Agent": "wolf_build"})
    payload = json.loads(read(req))
    for image in payload.get("images", []):
        if image.get("architecture") == "amd64" and image.get("os") == "linux":
            digest = image.get("digest", "")
            if re.fullmatch(r"sha256:[0-9a-f]{64}", digest or ""):
                return digest
    raise ValueError(f"{image}:{tag} has no amd64 linux digest")
