#!/usr/bin/env python3
"""Minimal, dependency-free webhook forwarder for Cognis findings.

Reads JSON findings on stdin and POSTs them to a URL (SIEM/Slack/Jira bridge).
Usage:  <tool> scan . --format json | python integrations/webhook.py --url URL
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--header", action="append", default=[], help="Key: Value")
    args = ap.parse_args()

    if not args.url.startswith(("http://", "https://")):
        print(
            f"error: --url must start with http:// or https:// (got {args.url!r})",
            file=sys.stderr,
        )
        return 2

    payload = sys.stdin.read()
    if not payload.strip():
        print("error: no data on stdin — pipe JSON findings into this command",
              file=sys.stderr)
        return 2

    # Validate that the payload is well-formed JSON before sending.
    try:
        json.loads(payload)
    except json.JSONDecodeError as exc:
        print(f"error: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 1

    encoded = payload.encode("utf-8")
    req = urllib.request.Request(args.url, data=encoded, method="POST")
    req.add_header("Content-Type", "application/json")
    for h in args.header:
        k, _, v = h.partition(":")
        if not k.strip():
            print(f"error: malformed --header value {h!r} (expected 'Key: Value')",
                  file=sys.stderr)
            return 2
        req.add_header(k.strip(), v.strip())

    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"posted {len(encoded)} bytes -> {r.status}")
        return 0
    except Exception as e:
        print(f"webhook error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
