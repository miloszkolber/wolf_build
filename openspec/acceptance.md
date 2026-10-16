# Promotion acceptance record

## Latest for operator testing

`latest` may be promoted before full game/session acceptance when explicitly approved by the operator. The protected manual workflow rechecks the exact digest's payload and HIGH/CRITICAL scan, stages a digest-preserving `tested-<digest>` tag, then advances `latest` without rebuilding. Leave `evidence_url` empty for this mode. This does not create an accepted-session record or authorize deployment by a maintenance worker. Scheduled builds still publish candidates only.

## Full acceptance

The manual promotion job consumes an operator-reviewed JSON document from an HTTPS URL. Store deployment-specific records outside this repository. The document must name the exact tested candidate and baseline digests, reviewer and test date. Select `wolf_runtime`, `wolf_steam` or `wolf_lutris` in the workflow. Application evidence must explicitly name the same `image_name`. All checks describe the complete streaming stack with that exact application candidate, not standalone frontend startup. It is evidence supplied by a responsible tester, not proof that a JSON file itself exercised hardware.

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

Required reviewers remain configured in `intel-acceptance`. The workflow checks that protection in both promotion modes and validates the digest-bound record whenever an evidence URL is supplied. Missing session evidence must never be reported as full acceptance, even when the operator authorizes a testing `latest`.
