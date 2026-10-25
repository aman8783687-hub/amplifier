#!/usr/bin/env python3
"""Publish, schedule, update and verify videos on any Amplifier-connected channel.

This is the CEO's signing hand: it does not produce anything. It takes a finished
file, validates the packaging, uploads it to exactly the channel(s) you name,
sets the thumbnail, and registers the upload with Amplifier so analytics can find
it again.

Safety defaults:
  * privacy defaults to private
  * public uploads require --yes
  * multi-channel uploads require --yes (duplicate content is a choice, not an accident)
  * every upload is registered with Amplifier unless --no-register is passed

Examples:
  python3 publish.py channels
  python3 publish.py token --channel "Business Mafia"
  python3 publish.py upload --video final/ep.mp4 --channel "Business Mafia" \
      --title "ढाबा वाला कितना कमाता है?" --description-file final/description.txt \
      --tags "business,hindi,dhaba" --thumbnail final/thumb.jpg --privacy private
  python3 publish.py upload --video final/ep.mp4 --channel "Business Mafia" \
      --publish-at 2026-10-30T18:00:00+05:30 --yes
  python3 publish.py update --channel "Business Mafia" --video-id dQw4w9WgXcQ \
      --title "New title" --thumbnail final/thumb2.jpg
  python3 publish.py status --video-id <amplifierVideoId> --wait 300

Auth: --api-key, $AMPLIFIER_API_KEY, $AMPLIFIER_API_KEY_FILE, or ~/.config/amplifier/agent_key
API:  --api-url, $AMPLIFIER_API_URL (default https://amplifier-api.onrender.com)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_API = "https://amplifier-api.onrender.com"
TERMINAL = ("succeeded", "failed")


class AmplifierError(RuntimeError):
    pass


def read_key(explicit=None):
    if explicit:
        return explicit
    if os.environ.get("AMPLIFIER_API_KEY"):
        return os.environ["AMPLIFIER_API_KEY"]
    candidates = []
    if os.environ.get("AMPLIFIER_API_KEY_FILE"):
        candidates.append(Path(os.environ["AMPLIFIER_API_KEY_FILE"]).expanduser())
    candidates.append(Path("~/.config/amplifier/agent_key").expanduser())
    for path in candidates:
        if path.is_file():
            key = path.read_text(encoding="utf-8").strip()
            if key:
                return key
    raise SystemExit(
        "No Amplifier API key. Set AMPLIFIER_API_KEY, or write the key to "
        "~/.config/amplifier/agent_key (create one in the Amplifier UI)."
    )


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
            raise AmplifierError(f"{method} {path} -> {r.status_code}: {err}")
        return r.json()

    def channels(self):
        return self.call("GET", "/api/channels")

    def token(self, channel_id):
        return self.call("GET", f"/api/channels/{channel_id}/token")

    def register(self, channel_id, youtube_video_id, metadata):
        return self.call("POST", "/api/publications/register", json={
            "channelId": channel_id,
            "youtubeVideoId": youtube_video_id,
            "metadata": metadata,
        })


def find_channel(amp, needle):
    channels = amp.channels()
    if not channels:
        raise SystemExit("No channels connected in Amplifier. Connect one in the dashboard first.")
    needle = (needle or "").strip().lower()
    for c in channels:
        if needle == (c.get("title") or "").strip().lower():
            return c
    for c in channels:
        if needle == (c.get("youtubeChannelId") or "").lower() or needle == str(c.get("_id", "")).lower():
            return c
    for c in channels:
        if needle in (c.get("title") or "").lower():
            return c
    raise SystemExit(f"Channel {needle!r} not found. Connected: {[c.get('title') for c in channels]}")


def parse_metadata_file(path):
    """Best-effort parser for a Title/Description/Tags/Privacy metadata file."""
    out = {}
    if not path:
        return out
    text = Path(path).expanduser().read_text(encoding="utf-8")
    current = None
    buckets = {}
    for line in text.splitlines():
        m = re.match(r"^\s*(Title|Description|Tags|Privacy)\s*:\s*(.*)$", line, re.I)
        if m:
            current = m.group(1).lower()
            buckets[current] = [m.group(2)]
        elif current and line.strip():
            buckets[current].append(line)
    if "title" in buckets:
        out["title"] = " ".join(x.strip() for x in buckets["title"]).strip()
    if "description" in buckets:
        out["description"] = "\n".join(buckets["description"]).strip()
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


def parse_publish_at(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise SystemExit(
            f"--publish-at must be ISO 8601 with a timezone, e.g. 2026-10-30T18:00:00+05:30 (got {value!r})"
        )
    if dt.tzinfo is None:
        raise SystemExit("--publish-at needs an explicit timezone offset, e.g. +05:30 or Z")
    if dt <= datetime.now(timezone.utc):
        raise SystemExit("--publish-at is in the past")
    return dt.isoformat()


def build_metadata(args):
    file_meta = parse_metadata_file(getattr(args, "metadata_file", None))
    title = (getattr(args, "title", None) or file_meta.get("title") or "").strip()
    if not title and getattr(args, "video", None):
        title = Path(args.video).stem.replace("_", " ").replace("-", " ").title()
    description = getattr(args, "description", None)
    if getattr(args, "description_file", None):
        description = Path(args.description_file).expanduser().read_text(encoding="utf-8")
    if description is None:
        description = file_meta.get("description", "")
    tags = getattr(args, "tags", None)
    if tags:
        tags = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
    else:
        tags = list(file_meta.get("tags", []))
    privacy = getattr(args, "privacy", None) or file_meta.get("privacy") or "private"
    publish_at = parse_publish_at(getattr(args, "publish_at", None))
    if publish_at:
        privacy = "private"
    return {
        "title": title,
        "description": description or "",
        "tags": tags,
        "privacy": privacy,
        "categoryId": str(getattr(args, "category", None) or "22"),
        "madeForKids": bool(getattr(args, "made_for_kids", False)),
        "publishAt": publish_at,
    }


def validate_metadata(md):
    errors, warnings = [], []
    title = md.get("title") or ""
    description = md.get("description") or ""
    tags = md.get("tags") or []
    privacy = md.get("privacy") or "private"
    if not title:
        errors.append("title is empty")
    if len(title) > 100:
        errors.append(f"title is {len(title)} characters; YouTube allows 100")
    if "<" in title or ">" in title:
        errors.append("title contains < or >, which YouTube rejects")
    if len(description) > 5000:
        errors.append(f"description is {len(description)} characters; YouTube allows 5,000")
    if len(",".join(tags)) > 500:
        errors.append(f"tags total {len(','.join(tags))} characters; YouTube allows 500")
    if privacy not in ("private", "unlisted", "public"):
        errors.append(f"privacy must be private, unlisted or public (got {privacy!r})")
    if md.get("publishAt") and privacy != "private":
        errors.append("--publish-at only works with private privacy")
    if len(title) > 70:
        warnings.append(f"title is {len(title)} chars; mobile search truncates around 70")
    if len(description) < 200 and privacy == "public":
        warnings.append("description is under 200 chars; that is thin for search")
    if not tags:
        warnings.append("no tags")
    return errors, warnings


def youtube_upload(video_path, md, access_token):
    size = video_path.stat().st_size
    body = {
        "snippet": {
            "title": md["title"],
            "description": md.get("description", ""),
            "tags": md.get("tags", []),
            "categoryId": str(md.get("categoryId", "22")),
        },
        "status": {
            "privacyStatus": md.get("privacy", "private"),
            "selfDeclaredMadeForKids": bool(md.get("madeForKids", False)),
        },
    }
    if md.get("publishAt"):
        body["status"]["publishAt"] = md["publishAt"]

    init = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(size),
        },
        json=body,
        timeout=60,
    )
    if not init.ok:
        raise RuntimeError(f"YouTube upload init failed ({init.status_code}): {init.text[:400]}")
    session_url = init.headers.get("Location")
    if not session_url:
        raise RuntimeError("YouTube did not return a resumable session URL")

    print(f"Uploading {video_path.name} ({size / 1048576:.1f} MiB)…", file=sys.stderr)
    with video_path.open("rb") as fh:
        done = requests.put(
            session_url,
            headers={"Content-Type": "video/mp4", "Content-Length": str(size)},
            data=fh,
            timeout=3600,
        )
    if not done.ok:
        raise RuntimeError(f"YouTube upload failed ({done.status_code}): {done.text[:400]}")
    payload = done.json()
    video_id = payload.get("id")
    if not video_id:
        raise RuntimeError(f"YouTube upload returned no video id: {payload}")
    return video_id


def set_thumbnail(video_id, thumbnail, access_token):
    path = Path(thumbnail).expanduser()
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    with path.open("rb") as fh:
        r = requests.post(
            "https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
            params={"videoId": video_id, "uploadType": "media"},
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": mime},
            data=fh,
            timeout=120,
        )
    if not r.ok:
        print(f"warning: thumbnail not set ({r.status_code}): {r.text[:200]}", file=sys.stderr)
        return False
    return True


def yt_call(method, path, access_token, **kwargs):
    r = requests.request(
        method,
        f"https://www.googleapis.com/youtube/v3/{path}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=120,
        **kwargs,
    )
    if not r.ok:
        raise RuntimeError(f"YouTube {method} {path} failed ({r.status_code}): {r.text[:400]}")
    return r.json()


def cmd_channels(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    channels = amp.channels()
    if args.json:
        print(json.dumps(channels, indent=2, ensure_ascii=False))
        return
    if not channels:
        print("No channels connected.")
        return
    print(f"{'CHANNEL':28} {'STATUS':16} {'YOUTUBE ID':26} AMPLIFIER ID")
    for c in channels:
        print(
            f"{(c.get('title') or '?')[:27]:28} {(c.get('status') or '?')[:15]:16} "
            f"{(c.get('youtubeChannelId') or '?')[:25]:26} {c.get('_id')}"
        )


def cmd_token(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    channel = find_channel(amp, args.channel)
    data = amp.token(channel["_id"])
    if args.raw:
        print(data["access_token"])
    else:
        print(json.dumps({
            "channel": channel.get("title"),
            "channelId": channel["_id"],
            **data,
        }, indent=2))


def cmd_upload(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    if args.all:
        targets = [c for c in amp.channels() if (c.get("status") or "connected") == "connected"]
    else:
        if not args.channel:
            raise SystemExit("Pass --channel NAME (repeatable), or --all to target every connected channel.")
        targets = [find_channel(amp, name) for name in args.channel]
    if not targets:
        raise SystemExit("No connected channels to publish to.")

    video = Path(args.video).expanduser().resolve()
    if not video.is_file():
        raise SystemExit(f"video not found: {video}")
    md = build_metadata(args)
    errors, warnings = validate_metadata(md)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        raise SystemExit(2)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    public_release = md["privacy"] == "public" or bool(md.get("publishAt"))
    if public_release and not args.yes and not args.dry_run:
        raise SystemExit(
            "A public or scheduled-public release requires --yes. Review the title, thumbnail and description first."
        )
    if len(targets) > 1 and not args.yes and not args.dry_run:
        raise SystemExit(
            f"This would publish to {len(targets)} channels. Duplicate content across channels is a strategy, "
            "not an accident — re-run with --yes if that is the deliberate call."
        )

    thumbnail = Path(args.thumbnail).expanduser().resolve() if args.thumbnail else None
    if thumbnail and not thumbnail.is_file():
        raise SystemExit(f"thumbnail not found: {thumbnail}")

    results = []
    for channel in targets:
        result = {
            "channel": channel.get("title"),
            "channelId": channel["_id"],
            "privacy": md["privacy"],
            "publishAt": md.get("publishAt"),
            "title": md["title"],
        }
        try:
            token = amp.token(channel["_id"])["access_token"]
            if args.dry_run:
                result.update({"dryRun": True, "tokenMinted": True, "video": str(video), "sizeBytes": video.stat().st_size})
                result["ok"] = True
                results.append(result)
                continue
            youtube_video_id = youtube_upload(video, md, token)
            result["youtubeVideoId"] = youtube_video_id
            result["youtubeUrl"] = f"https://youtu.be/{youtube_video_id}"
            if thumbnail:
                result["thumbnailSet"] = set_thumbnail(youtube_video_id, thumbnail, token)
            if not args.no_register:
                try:
                    registered = amp.register(channel["_id"], youtube_video_id, {
                        "title": md["title"],
                        "description": md.get("description", ""),
                        "tags": md.get("tags", []),
                        "privacy": md["privacy"],
                    })
                    result["amplifierVideoId"] = registered.get("videoId")
                    result["publicationId"] = registered.get("publicationId")
                except Exception as e:
                    result["registerError"] = str(e)
            result["ok"] = True
        except Exception as e:
            result["ok"] = False
            result["error"] = str(e)
        results.append(result)
        status = "DRY RUN" if args.dry_run else ("OK" if result.get("ok") else "FAILED")
        print(f"{status}: {channel.get('title')}" + (f" → {result.get('youtubeUrl')}" if result.get("youtubeUrl") else ""), file=sys.stderr)

    print(json.dumps({"uploaded": sum(1 for r in results if r.get("ok")), "results": results}, indent=2, ensure_ascii=False))
    return 0 if all(r.get("ok") for r in results) else 1


def cmd_update(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    channel = find_channel(amp, args.channel)
    token = amp.token(channel["_id"])["access_token"]

    current = yt_call("GET", "videos", token, params={
        "part": "snippet,status",
        "id": args.video_id,
    })
    items = current.get("items") or []
    if not items:
        raise SystemExit(f"Video {args.video_id} not found on {channel.get('title')} (wrong channel or id?)")
    item = items[0]
    snippet = item.get("snippet") or {}
    status = item.get("status") or {}

    new_snippet = {
        k: snippet.get(k) for k in (
            "title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage",
        ) if snippet.get(k) is not None
    }
    if args.title is not None:
        new_snippet["title"] = args.title
    if args.description_file:
        new_snippet["description"] = Path(args.description_file).expanduser().read_text(encoding="utf-8")
    elif args.description is not None:
        new_snippet["description"] = args.description
    if args.tags is not None:
        new_snippet["tags"] = [t.strip().lstrip("#") for t in args.tags.split(",") if t.strip()]
    if args.category is not None:
        new_snippet["categoryId"] = str(args.category)

    new_status = {
        k: status.get(k) for k in (
            "privacyStatus", "selfDeclaredMadeForKids", "license", "embeddable", "publicStatsViewable",
        ) if status.get(k) is not None
    }
    if args.privacy:
        if args.privacy == "public" and not args.yes:
            raise SystemExit("Making a video public requires --yes.")
        new_status["privacyStatus"] = args.privacy
    if args.publish_at:
        if not args.yes and not args.dry_run:
            raise SystemExit("Scheduling a public release requires --yes.")
        new_status["privacyStatus"] = "private"
        new_status["publishAt"] = parse_publish_at(args.publish_at)
    if args.made_for_kids is not None:
        new_status["selfDeclaredMadeForKids"] = args.made_for_kids

    merged = {
        "title": new_snippet.get("title", ""),
        "description": new_snippet.get("description", ""),
        "tags": new_snippet.get("tags", []),
        "privacy": new_status.get("privacyStatus", "private"),
    }
    errors, warnings = validate_metadata(merged)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        raise SystemExit(2)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    if args.dry_run:
        print(json.dumps({"dryRun": True, "channel": channel.get("title"), "videoId": args.video_id,
                          "snippet": new_snippet, "status": new_status}, indent=2, ensure_ascii=False))
        return 0

    updated = yt_call("PUT", "videos", token, params={"part": "snippet,status"}, json={
        "id": args.video_id,
        "snippet": new_snippet,
        "status": new_status,
    })
    result = {
        "ok": True,
        "channel": channel.get("title"),
        "videoId": args.video_id,
        "title": (updated.get("snippet") or {}).get("title"),
        "privacy": (updated.get("status") or {}).get("privacyStatus"),
        "publishAt": (updated.get("status") or {}).get("publishAt"),
    }
    if args.thumbnail:
        thumb = Path(args.thumbnail).expanduser().resolve()
        if not thumb.is_file():
            raise SystemExit(f"thumbnail not found: {thumb}")
        result["thumbnailSet"] = set_thumbnail(args.video_id, thumb, token)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cmd_register(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    channel = find_channel(amp, args.channel)
    md = build_metadata(args)
    errors, _ = validate_metadata(md)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        raise SystemExit(2)
    registered = amp.register(channel["_id"], args.youtube_video_id, {
        "title": md["title"],
        "description": md.get("description", ""),
        "tags": md.get("tags", []),
        "privacy": md["privacy"],
    })
    print(json.dumps({"channel": channel.get("title"), **registered}, indent=2, ensure_ascii=False))


def cmd_status(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    deadline = time.time() + max(args.wait, 0)
    while True:
        pubs = amp.call("GET", f"/api/publications?videoId={args.video_id}")
        if not pubs:
            print(json.dumps({"videoId": args.video_id, "publications": []}, indent=2))
            return 1
        print(json.dumps({"videoId": args.video_id, "publications": pubs}, indent=2, ensure_ascii=False))
        if all(p.get("status") in TERMINAL for p in pubs) or time.time() >= deadline:
            break
        time.sleep(5)
    return 0 if all(p.get("status") == "succeeded" for p in pubs) else 1


def cmd_analytics(args):
    amp = Amplifier(args.api_url, read_key(args.api_key))
    if args.overview:
        data = amp.call("GET", f"/api/analytics/overview?range={args.range}")
    elif args.video:
        data = amp.call("GET", f"/api/analytics/videos/{args.video}?range={args.range}")
    else:
        if not args.channel:
            raise SystemExit("Pass --channel, --overview, or --video.")
        channel = find_channel(amp, args.channel)
        data = amp.call("GET", f"/api/analytics/channels/{channel['_id']}?range={args.range}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def add_common(parser):
    parser.add_argument("--api-url", default=os.environ.get("AMPLIFIER_API_URL", DEFAULT_API))
    parser.add_argument("--api-key")


def main():
    common = argparse.ArgumentParser(add_help=False)
    add_common(common)
    parser = argparse.ArgumentParser(description="Publish and manage videos on Amplifier-connected YouTube channels")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("channels", parents=[common], help="list connected channels")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_channels)

    p = sub.add_parser("token", parents=[common], help="mint a short-lived YouTube access token")
    p.add_argument("--channel", required=True)
    p.add_argument("--raw", action="store_true", help="print only the token")
    p.set_defaults(func=cmd_token)

    p = sub.add_parser("upload", parents=[common], help="upload a finished video")
    p.add_argument("--video", required=True)
    p.add_argument("--channel", action="append", help="channel name/id (repeatable)")
    p.add_argument("--all", action="store_true", help="every connected channel (requires --yes)")
    p.add_argument("--title")
    p.add_argument("--description")
    p.add_argument("--description-file")
    p.add_argument("--tags", help="comma-separated")
    p.add_argument("--thumbnail")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"], default=None)
    p.add_argument("--publish-at", help="ISO 8601 with timezone; implies private")
    p.add_argument("--category", default="22", help="YouTube category id (default 22, People & Blogs)")
    p.add_argument("--made-for-kids", action="store_true")
    p.add_argument("--metadata-file", help="optional Title/Description/Tags/Privacy file")
    p.add_argument("--no-register", action="store_true", help="do not register the upload with Amplifier")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true", help="confirm public or multi-channel publishing")
    p.set_defaults(func=cmd_upload)

    p = sub.add_parser("update", parents=[common], help="edit title/description/tags/privacy/thumbnail")
    p.add_argument("--channel", required=True)
    p.add_argument("--video-id", required=True, help="YouTube video id")
    p.add_argument("--title")
    p.add_argument("--description")
    p.add_argument("--description-file")
    p.add_argument("--tags")
    p.add_argument("--thumbnail")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"])
    p.add_argument("--publish-at")
    p.add_argument("--category")
    p.add_argument("--made-for-kids", dest="made_for_kids", action="store_true", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("register", parents=[common], help="register an existing YouTube upload with Amplifier")
    p.add_argument("--channel", required=True)
    p.add_argument("--youtube-video-id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description")
    p.add_argument("--description-file")
    p.add_argument("--tags")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    p.add_argument("--metadata-file")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("status", parents=[common], help="poll publication status by Amplifier video id")
    p.add_argument("--video-id", required=True, help="Amplifier videoId")
    p.add_argument("--wait", type=int, default=0, help="seconds to keep polling")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("analytics", parents=[common], help="read Amplifier analytics")
    p.add_argument("--channel")
    p.add_argument("--overview", action="store_true")
    p.add_argument("--video", help="Amplifier videoId")
    p.add_argument("--range", default="28d", choices=["7d", "28d", "90d"])
    p.set_defaults(func=cmd_analytics)

    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
