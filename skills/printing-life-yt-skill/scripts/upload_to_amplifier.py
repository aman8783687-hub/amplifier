#!/usr/bin/env python3
"""Upload a finished Printing Life video to ONE YouTube channel via Amplifier.

Default path: mint a short-lived YouTube access token from Amplifier, stream the
local file straight to YouTube (no Cloudinary/Render memory ceiling), then
register the upload with Amplifier so its analytics sync can track the video.

Usage:
  python3 upload_to_amplifier.py \
    --video final/my-video.mp4 \
    --title "The French Revolution (Part 1)" \
    --description-file final/description.txt \
    --tags "history,french revolution,animated history" \
    --privacy public \
    --thumbnail final/thumbnail.jpg \
    --channel "Printing Life"

Auth: --api-key, or $AMPLIFIER_API_KEY, or ~/.config/amplifier/agent_key.
API:  --api-url, or $AMPLIFIER_API_URL (default https://amplifier-api.onrender.com).
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

DEFAULT_API = "https://amplifier-api.onrender.com"
DEFAULT_CHANNEL = "Printing Life"


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


def _normalize_description(lines):
    """Join hard-wrapped paragraphs while keeping chapters, bullets and headings.

    Descriptions are often written wrapped at 80 columns. YouTube would show
    every one of those breaks, so prose lines are joined with a space; blank
    lines, timestamps, bullets, hashtags and ALL-CAPS headings stay separate.
    """
    out = []
    buf = []

    def flush():
        if buf:
            out.append(" ".join(x.strip() for x in buf))
            buf.clear()

    for raw in lines:
        s = raw.strip()
        if not s:
            flush()
            if out and out[-1] != "":
                out.append("")
            continue
        structural = (
            re.match(r"^\d{1,2}:\d{2}", s)
            or s.startswith(("-", "•", "#"))
            or s.isupper()
        )
        if structural:
            flush()
            out.append(s)
        else:
            buf.append(s)
    flush()
    return "\n".join(out).strip()


def parse_metadata_file(path):
    """Best-effort parser for the skill's final_upload_metadata.txt."""
    out = {}
    if not path:
        return out
    text = Path(path).read_text(encoding="utf-8")
    current = None
    buckets = {}
    for line in text.splitlines():
        m = re.match(r"^\s*(Title|Description|Tags|Privacy)\s*:\s*(.*)$", line, re.I)
        if m:
            current = m.group(1).lower()
            buckets[current] = [m.group(2)]
        elif current:
            # Keep blank lines in the description; YouTube chapters and
            # paragraphs need them. Other buckets ignore blanks later.
            buckets[current].append(line.rstrip())
    if "title" in buckets:
        out["title"] = " ".join(x.strip() for x in buckets["title"]).strip()
    if "description" in buckets:
        out["description"] = _normalize_description(buckets["description"])
    if "tags" in buckets:
        raw = ",".join(buckets["tags"])
        if "," in raw:
            tags = [t.strip() for t in raw.split(",")]
        else:
            tags = [t.strip() for t in re.split(r"\s+", raw)]
        out["tags"] = [t.lstrip("#").strip() for t in tags if t.strip()]
    if "privacy" in buckets:
        out["privacy"] = buckets["privacy"][0].strip().lower()
    return out


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

    def channels(self):
        return self.call("GET", "/api/channels")

    def find_channel(self, name):
        channels = self.channels()
        if not channels:
            raise RuntimeError("No channels connected in Amplifier. Connect one in the dashboard first.")
        exact = [c for c in channels if (c.get("title") or "").strip().lower() == name.strip().lower()]
        if exact:
            return exact[0]
        partial = [c for c in channels if name.strip().lower() in (c.get("title") or "").lower()]
        if partial:
            return partial[0]
        names = [c.get("title") for c in channels]
        raise RuntimeError(f"Channel {name!r} not found. Connected channels: {names}")

    def access_token(self, channel_id):
        data = self.call("GET", f"/api/channels/{channel_id}/token")
        return data["access_token"]

    def register(self, channel_id, youtube_video_id, metadata):
        return self.call("POST", "/api/publications/register", json={
            "channelId": channel_id,
            "youtubeVideoId": youtube_video_id,
            "metadata": metadata,
        })


def youtube_resumable_upload(video_path, metadata, access_token):
    size = video_path.stat().st_size
    init = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(size),
        },
        json={
            "snippet": {
                "title": metadata["title"],
                "description": metadata.get("description", ""),
                "tags": metadata.get("tags", []),
                "categoryId": str(metadata.get("categoryId", "22")),
            },
            "status": {"privacyStatus": metadata.get("privacy", "private")},
        },
        timeout=60,
    )
    if not init.ok:
        raise RuntimeError(f"YouTube upload init failed ({init.status_code}): {init.text[:300]}")
    session_url = init.headers.get("Location")
    if not session_url:
        raise RuntimeError("YouTube did not return a resumable session URL")

    print(f"Uploading {video_path.name} ({size / 1048576:.1f} MiB) to YouTube…", file=sys.stderr)
    with video_path.open("rb") as fh:
        done = requests.put(
            session_url,
            headers={"Content-Type": "video/mp4", "Content-Length": str(size)},
            data=fh,
            timeout=3600,
        )
    if not done.ok:
        raise RuntimeError(f"YouTube upload failed ({done.status_code}): {done.text[:300]}")
    body = done.json()
    video_id = body.get("id")
    if not video_id:
        raise RuntimeError(f"YouTube upload returned no video id: {body}")
    return video_id


def youtube_set_thumbnail(video_id, thumbnail_path, access_token):
    with thumbnail_path.open("rb") as fh:
        r = requests.post(
            "https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
            params={"videoId": video_id, "uploadType": "media"},
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "image/jpeg"},
            data=fh,
            timeout=120,
        )
    if not r.ok:
        print(f"warning: thumbnail not set ({r.status_code}): {r.text[:200]}", file=sys.stderr)
        return False
    return True


def publish_via_cloudinary(amp, channel, video_path, metadata):
    print("Uploading via Cloudinary staging…", file=sys.stderr)
    with video_path.open("rb") as fh:
        r = amp.session.post(
            amp.base + "/api/videos",
            files={"file": (video_path.name, fh, "video/mp4")},
            timeout=3600,
        )
    if not r.ok:
        try:
            err = r.json().get("error")
        except Exception:
            err = r.text[:300]
        raise RuntimeError(f"Cloudinary staging failed ({r.status_code}): {err}")
    staged = r.json()
    amp.call("POST", "/api/publications", json={
        "videoId": staged["videoId"],
        "channelIds": [channel["_id"]],
        "metadata": metadata,
    })
    for _ in range(180):
        pubs = amp.call("GET", f"/api/publications?videoId={staged['videoId']}")
        if pubs and all(p.get("status") in ("succeeded", "failed") for p in pubs):
            pub = pubs[0]
            if pub.get("status") == "failed":
                raise RuntimeError(f"YouTube upload failed: {pub.get('error')}")
            return staged["videoId"], pub.get("youtubeVideoId")
        time.sleep(5)
    raise RuntimeError("Timed out waiting for publication (still processing in background)")


def main():
    ap = argparse.ArgumentParser(description="Upload one video to one connected YouTube channel via Amplifier")
    ap.add_argument("--video", required=True, help="finished .mp4 file")
    ap.add_argument("--thumbnail", help="thumbnail image (jpg/png)")
    ap.add_argument("--title")
    ap.add_argument("--description")
    ap.add_argument("--description-file")
    ap.add_argument("--tags", help="comma-separated")
    ap.add_argument("--privacy", choices=["private", "unlisted", "public"], default=None)
    ap.add_argument("--metadata-file", help="optional Title/Description/Tags/Privacy file")
    ap.add_argument("--channel", default=os.environ.get("AMPLIFIER_CHANNEL", DEFAULT_CHANNEL))
    ap.add_argument("--api-url", default=os.environ.get("AMPLIFIER_API_URL", DEFAULT_API))
    ap.add_argument("--api-key")
    ap.add_argument("--via-cloudinary", action="store_true", help="stage on Cloudinary and let the server upload")
    ap.add_argument("--analytics", action="store_true", help="fetch analytics after registering")
    ap.add_argument("--wait", type=int, default=0, help="seconds to wait before fetching analytics")
    ap.add_argument("--dry-run", action="store_true", help="resolve channel + token, validate metadata, do not upload")
    args = ap.parse_args()

    video_path = Path(args.video).expanduser().resolve()
    if not video_path.is_file():
        sys.exit(f"video not found: {video_path}")

    file_meta = parse_metadata_file(args.metadata_file)
    title = args.title or file_meta.get("title") or video_path.stem.replace("_", " ").replace("-", " ").title()
    description = args.description
    if args.description_file:
        description = Path(args.description_file).read_text(encoding="utf-8")
    if description is None:
        description = file_meta.get("description", "")
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else list(file_meta.get("tags", []))
    privacy = args.privacy or file_meta.get("privacy") or "private"
    metadata = {"title": title, "description": description, "tags": tags, "privacy": privacy}

    key = read_key(args)
    amp = Amplifier(args.api_url, key)
    channel = amp.find_channel(args.channel)
    print(f"Target channel: {channel.get('title')} ({channel['_id']})", file=sys.stderr)

    token = amp.access_token(channel["_id"])

    if args.dry_run:
        print(json.dumps({
            "dryRun": True,
            "channel": channel.get("title"),
            "channelId": channel["_id"],
            "video": str(video_path),
            "sizeBytes": video_path.stat().st_size,
            "thumbnail": str(Path(args.thumbnail).expanduser().resolve()) if args.thumbnail else None,
            "metadata": metadata,
            "tokenMinted": bool(token),
        }, indent=2))
        return

    if args.via_cloudinary:
        amplifier_video_id, youtube_video_id = publish_via_cloudinary(amp, channel, video_path, metadata)
        registered = {"videoId": amplifier_video_id}
    else:
        youtube_video_id = youtube_resumable_upload(video_path, metadata, token)
        registered = amp.register(channel["_id"], youtube_video_id, metadata)
        amplifier_video_id = registered["videoId"]

    thumbnail_ok = None
    if args.thumbnail:
        thumb = Path(args.thumbnail).expanduser().resolve()
        if thumb.is_file():
            thumbnail_ok = youtube_set_thumbnail(youtube_video_id, thumb, token)

    result = {
        "channel": channel.get("title"),
        "channelId": channel["_id"],
        "youtubeVideoId": youtube_video_id,
        "youtubeUrl": f"https://youtu.be/{youtube_video_id}",
        "amplifierVideoId": amplifier_video_id,
        "thumbnailSet": thumbnail_ok,
        "privacy": privacy,
        "title": title,
    }

    if args.analytics:
        if args.wait:
            time.sleep(args.wait)
        try:
            result["analytics"] = amp.call("GET", f"/api/analytics/videos/{amplifier_video_id}?range=28d")
        except Exception as e:
            result["analyticsError"] = str(e)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
