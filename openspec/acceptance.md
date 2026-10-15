# Promotion acceptance record

The manual promotion job consumes an operator-reviewed JSON document from an HTTPS URL. Store deployment-specific records outside this repository. The document must name the exact tested candidate and baseline digests, reviewer and test date. It is evidence supplied by a responsible tester, not proof that a JSON file itself exercised hardware.

```json
{
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

Required reviewers must be configured in the repository's `intel-acceptance` environment. The workflow checks that configuration as well as the digest-bound record. No available GPU runner, missing evidence or pending manual review is a reason to publish a candidate as `latest`.
