"""Validate full-session acceptance evidence independently of image publication."""
import argparse
import json
import re
from pathlib import Path

CHECKS = ("static", "cold_tcp", "cold_udp", "pairing_reconnect", "audio", "keyboard_mouse", "controller", "steam_lutris", "sustained_stream", "latency_quality", "idle_stop", "drm_release")


def validate(record, digest, image="wolf_runtime"):
    if image not in ("wolf_runtime", "wolf_steam", "wolf_lutris") or record.get("image_name", "wolf_runtime") != image:
        raise ValueError("acceptance belongs to a different image repository")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}",digest):
        raise ValueError("candidate must be an exact SHA256 image digest")
    if record.get("image_digest") != digest:
        raise ValueError("acceptance belongs to a different image")
    if record.get("status") != "accepted" or not record.get("reviewer") or not record.get("tested_at") or not record.get("baseline_digest"):
        raise ValueError("acceptance needs status, reviewer, test date and baseline")
    checks = record.get("checks",{})
    if any(checks.get(check) != "pass" for check in CHECKS):
        raise ValueError("required session checks have not all passed")
    codecs = record.get("codecs",{})
    for codec in ("h264","hevc","av1"):
        result=codecs.get(codec,{})
        if result.get("supported") is True:
            if result.get("hardware_encoding") != "pass" or result.get("zero_copy") != "pass":
                raise ValueError("supported codec lacks hardware/zero-copy evidence: "+codec)
        elif result.get("supported") is not False or not result.get("capability_evidence"):
            raise ValueError("unsupported codec needs capability evidence: "+codec)
    if not any(codecs[c].get("supported") for c in ("h264","hevc","av1")):
        raise ValueError("no codec tested")
    return True


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("evidence",type=Path)
    parser.add_argument("digest")
    parser.add_argument("--image", choices=("wolf_runtime", "wolf_steam", "wolf_lutris"), default="wolf_runtime")
    args=parser.parse_args()
    validate(json.loads(args.evidence.read_text()),args.digest,args.image)
    print("Full-session acceptance record matches the image; no publication or deployment performed.")


if __name__ == "__main__": main()
