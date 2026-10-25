#!/usr/bin/env python3
"""Read Business Mafia channel/video analytics from Amplifier.

Examples:
  python3 amplifier_analytics.py --channel "Business Mafia"
  python3 amplifier_analytics.py --channel "Business Mafia" --range 7d
  python3 amplifier_analytics.py --video <amplifierVideoId>
  python3 amplifier_analytics.py --overview
  python3 amplifier_analytics.py --channel "Business Mafia" --refresh

Auth: --api-key, or $AMPLIFIER_API_KEY, or ~/.config/amplifier/agent_key.
API:  --api-url, or $AMPLIFIER_API_URL (default https://amplifier-api.onrender.com).
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

DEFAULT_API = "https://amplifier-api.onrender.com"
DEFAULT_CHANNEL = "Business Mafia"


def read_key(args):
    if args.api_key:
        return args.api_key
    if os.environ.get("AMPLIFIER_API_KEY"):
        return os.environ["AMPLIFIER_API_KEY"]
    candidates = []
    if os.environ.get("AMPLIFIER_API_KEY_FILE"):
        candidates.append(Path(os.environ["AMPLIFIER_API_KEY_FILE"]))
    candidates.append(Path.home() / ".config" / "amplifier" / "agent_key")
    for path in candidates:
        if path.is_file():
            key = path.read_text().strip()
            if key:
                return key
    sys.exit("No Amplifier API key. Set AMPLIFIER_API_KEY or write ~/.config/amplifier/agent_key")


class Amplifier:
    def __init__(self, base_url, key):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {key}"})

    def call(self, method, path, timeout=120, **kwargs):
        r = self.session.request(method, self.base + path, timeout=timeout, **kwargs)
        if not r.ok:
            try:
                err = r.json().get("error")
            except Exception:
                err = r.text[:300]
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {err}")
        return r.json()

    def find_channel(self, name):
        channels = self.call("GET", "/api/channels")
        if not channels:
            raise RuntimeError("No channels connected in Amplifier.")
        for c in channels:
            if (c.get("title") or "").strip().lower() == name.strip().lower():
                return c
        for c in channels:
            if name.strip().lower() in (c.get("title") or "").lower():
                return c
        raise RuntimeError(f"Channel {name!r} not found. Connected: {[c.get('title') for c in channels]}")


def main():
    ap = argparse.ArgumentParser(description="Read Amplifier analytics")
    ap.add_argument("--channel", default=os.environ.get("AMPLIFIER_CHANNEL", DEFAULT_CHANNEL))
    ap.add_argument("--video", help="Amplifier videoId (from upload output)")
    ap.add_argument("--overview", action="store_true", help="all videos/channels")
    ap.add_argument("--range", default="28d", choices=["7d", "28d", "90d"])
    ap.add_argument("--refresh", action="store_true", help="ask Amplifier to pull fresh stats from YouTube")
    ap.add_argument("--api-url", default=os.environ.get("AMPLIFIER_API_URL", DEFAULT_API))
    ap.add_argument("--api-key")
    args = ap.parse_args()

    amp = Amplifier(args.api_url, read_key(args))

    if args.refresh:
        payload = {"videoId": args.video} if args.video else {}
        refresh = amp.call("POST", "/api/analytics/refresh", json=payload)
    else:
        refresh = None

    if args.video:
        data = amp.call("GET", f"/api/analytics/videos/{args.video}?range={args.range}")
    elif args.overview:
        data = amp.call("GET", f"/api/analytics/overview?range={args.range}")
    else:
        channel = amp.find_channel(args.channel)
        data = amp.call("GET", f"/api/analytics/channels/{channel['_id']}")

    out = {"refresh": refresh, "analytics": data}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
