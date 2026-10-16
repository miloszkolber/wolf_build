# Full-session acceptance record

## Publication is separate

Default-channel builds automatically publish checked images to an immutable input-hash tag and the same digest as `latest`. There is no manual promotion workflow, evidence URL or `tested-` tag. Payload/session smoke checks, SBOM and HIGH/CRITICAL scans gate publication. Full real-game acceptance is not implied by `latest` and does not block routine checked-image updates. Explicit Wolf source overrides remain candidate-only.

## Full acceptance

Store deployment-specific acceptance records outside this repository. Each record must name the exact tested image and baseline digests, image name, reviewer and test date. Validate it with `python3 scripts/promotion.py evidence.json sha256:<digest> --image wolf_runtime` (or `wolf_steam`/`wolf_lutris`). All checks describe the complete streaming stack with that exact candidate, not standalone frontend startup. This validates a responsible tester's record, not proof that JSON itself exercised hardware.

```json
{
  "image_name": "wolf_runtime",
  "image_digest": "sha256:<64 hexadecimal characters>",
  "baseline_digest": "sha256:<64 hexadecimal characters>",
  "reviewer": "responsible tester",
  "tested_at": "ISO date or timestamp",
  "status": "accepted",
  "checks": {
    "static": "pass",
    "cold_tcp": "pass",
    "cold_udp": "pass",
    "pairing_reconnect": "pass",
    "audio": "pass",
    "keyboard_mouse": "pass",
    "controller": "pass",
    "steam_lutris": "pass",
    "sustained_stream": "pass",
    "latency_quality": "pass",
    "idle_stop": "pass",
    "drm_release": "pass"
  },
  "codecs": {
    "h264": {"supported": true, "hardware_encoding": "pass", "zero_copy": "pass"},
    "hevc": {"supported": true, "hardware_encoding": "pass", "zero_copy": "pass"},
    "av1": {"supported": false, "capability_evidence": "pointer to actual driver capability evidence"}
  }
}
```

This is a format example, not an acceptance result. Each advertised codec must pass hardware encoding and zero-copy checks. Unsupported codecs require capability evidence, not a convenient skip. A software encoder fallback cannot count as hardware acceptance. At least one codec must be tested. Record baseline tolerances and full session observations with the external evidence.

Missing session evidence must never be reported as full acceptance. A complete record is acceptance bookkeeping, not an extra publication or host-deployment workflow.
