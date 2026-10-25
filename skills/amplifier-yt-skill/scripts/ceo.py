#!/usr/bin/env python3
"""Amplifier CEO — the portfolio ledger and review engine for all connected channels.

One SQLite database, one report, one place where every channel is compared on the
same terms. This script is deliberately boring: it pulls truth from Amplifier and
the YouTube APIs, stores a snapshot, and prints the numbers a CEO needs to make a
call. Strategy lives in SKILL.md, not in this file.

Examples:
  python3 ceo.py doctor
  python3 ceo.py sync
  python3 ceo.py report
  python3 ceo.py report --out ~/.amplifier/ceo/reports/2026-10-21.md
  python3 ceo.py channels
  python3 ceo.py channel-set --channel "RedHat Engineer" --tier build --cadence 2
  python3 ceo.py log --channel "Business Mafia" --decision "Fix packaging before next upload" --why "2 of last 3 under 60% of typical" --review-on 2026-11-04
  python3 ceo.py task-add --channel "Wild Thinking" --title "Commission lighthouse sequel" --due 2026-10-28
  python3 ceo.py tasks
  python3 ceo.py slate-add --channel "Business Mafia" --publish-on 2026-10-27 --title "Dhaba wala kitna kamata hai?" --format kamai
  python3 ceo.py slate
  python3 ceo.py history --channel "RedHat Engineer"
  python3 ceo.py playbook --channel "RedHat Engineer"

State: $AMPLIFIER_CEO_HOME (default ~/.amplifier/ceo)
Auth: --api-key, $AMPLIFIER_API_KEY, $AMPLIFIER_API_KEY_FILE, or ~/.config/amplifier/agent_key
API:  --api-url, $AMPLIFIER_API_URL (default https://amplifier-api.onrender.com)
"""

import argparse
import json
import os
import re
import sqlite3
import statistics
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

DEFAULT_API = "https://amplifier-api.onrender.com"
DEFAULT_SKILLS = {
    "business mafia": "business-mafia-yt-skill",
    "wild thinking": "wild-thinking-yt-skill",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS channels (
  id INTEGER PRIMARY KEY,
  youtube_id TEXT UNIQUE NOT NULL,
  amplifier_id TEXT,
  title TEXT,
  handle TEXT,
  description TEXT,
  thumbnail TEXT,
  tier TEXT NOT NULL DEFAULT 'bet',
  tier_locked INTEGER NOT NULL DEFAULT 0,
  cadence_per_week REAL NOT NULL DEFAULT 1,
  pillar TEXT,
  owner_skill TEXT,
  status TEXT NOT NULL DEFAULT 'connected',
  notes TEXT,
  first_seen TEXT,
  last_synced TEXT,
  analytics_status TEXT,
  analytics_error TEXT
);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY,
  channel_id INTEGER NOT NULL,
  taken_at TEXT NOT NULL,
  range_days INTEGER NOT NULL,
  subs INTEGER,
  total_views INTEGER,
  video_count INTEGER,
  period_views INTEGER,
  period_watch_minutes INTEGER,
  period_subs_gained INTEGER,
  period_subs_lost INTEGER,
  avg_view_duration_sec REAL,
  uploads_in_period INTEGER,
  new_video_views INTEGER,
  typical_views INTEGER,
  momentum REAL,
  subs_delta INTEGER,
  analytics_ok INTEGER NOT NULL DEFAULT 0,
  data_source TEXT
);
CREATE TABLE IF NOT EXISTS videos (
  channel_id INTEGER NOT NULL,
  youtube_video_id TEXT NOT NULL,
  title TEXT,
  published_at TEXT,
  duration_sec INTEGER,
  views INTEGER,
  likes INTEGER,
  comments INTEGER,
  period_views INTEGER,
  period_watch_minutes INTEGER,
  period_subs_gained INTEGER,
  first_seen TEXT,
  last_seen TEXT,
  PRIMARY KEY (channel_id, youtube_video_id)
);
CREATE TABLE IF NOT EXISTS daily (
  channel_id INTEGER NOT NULL,
  day TEXT NOT NULL,
  views INTEGER,
  watch_minutes INTEGER,
  subs_gained INTEGER,
  subs_lost INTEGER,
  PRIMARY KEY (channel_id, day)
);
CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY,
  channel_id INTEGER,
  made_at TEXT NOT NULL,
  decision TEXT NOT NULL,
  rationale TEXT NOT NULL,
  review_on TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  outcome TEXT
);
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY,
  channel_id INTEGER,
  title TEXT NOT NULL,
  owner TEXT,
  due TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TEXT NOT NULL,
  done_at TEXT
);
CREATE TABLE IF NOT EXISTS slate (
  id INTEGER PRIMARY KEY,
  channel_id INTEGER,
  publish_on TEXT NOT NULL,
  title TEXT NOT NULL,
  format TEXT,
  status TEXT NOT NULL DEFAULT 'planned',
  notes TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sync_runs (
  id INTEGER PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  ok INTEGER,
  failed INTEGER,
  detail TEXT
);
"""


# --------------------------------------------------------------------------- #
# Small utilities
# --------------------------------------------------------------------------- #

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today_iso():
    return date.today().isoformat()


def ceo_home():
    return Path(os.environ.get("AMPLIFIER_CEO_HOME", "~/.amplifier/ceo")).expanduser()


def db_path():
    return ceo_home() / "ceo.db"


def ensure_dirs():
    for sub in ("", "reports", "channels", "logs"):
        (ceo_home() / sub).mkdir(parents=True, exist_ok=True)


def connect():
    ensure_dirs()
    con = sqlite3.connect(db_path())
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    ensure_columns(con)
    return con


def ensure_columns(con):
    """Additive migrations, so an older ceo.db keeps working."""
    wanted = {
        "channels": [
            ("handle", "TEXT"), ("description", "TEXT"), ("tier_locked", "INTEGER NOT NULL DEFAULT 0"),
            ("cadence_per_week", "REAL NOT NULL DEFAULT 1"), ("pillar", "TEXT"),
            ("owner_skill", "TEXT"), ("notes", "TEXT"), ("analytics_status", "TEXT"),
            ("analytics_error", "TEXT"),
        ],
        "snapshots": [
            ("new_video_views", "INTEGER"), ("typical_views", "INTEGER"), ("momentum", "REAL"),
            ("subs_delta", "INTEGER"), ("analytics_ok", "INTEGER NOT NULL DEFAULT 0"),
            ("data_source", "TEXT"),
        ],
        "videos": [
            ("period_views", "INTEGER"), ("period_watch_minutes", "INTEGER"),
            ("period_subs_gained", "INTEGER"),
        ],
    }
    for table, cols in wanted.items():
        existing = {r["name"] for r in con.execute(f"PRAGMA table_info({table})")}
        for name, decl in cols:
            if name not in existing:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")


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


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def median(values):
    clean = [v for v in values if v is not None]
    return statistics.median(clean) if clean else None


def parse_duration(text):
    if not text:
        return None
    m = re.fullmatch(r"P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", text)
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def days_since(iso):
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - dt).days)


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "channel").lower()).strip("-")
    return s or "channel"


def fmt_int(value):
    return "—" if value is None else f"{value:,}"


def fmt_momentum(value):
    return "—" if value is None else f"{value:.2f}×"


def fmt_signed(value):
    if value is None:
        return "—"
    return f"+{value:,}" if value > 0 else f"{value:,}"


def shorten(text, limit=72):
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


# --------------------------------------------------------------------------- #
# Amplifier + YouTube clients
# --------------------------------------------------------------------------- #

class AmplifierError(RuntimeError):
    pass


class YouTubeError(RuntimeError):
    def __init__(self, status, reason, message, url=None):
        self.status = status
        self.reason = reason or ""
        self.message = message or ""
        self.enable_url = url
        super().__init__(f"YouTube API {status} {self.reason}: {self.message}".strip())

    def is_analytics_disabled(self):
        blob = f"{self.reason} {self.message}".lower()
        return (
            "has not been used in project" in blob
            or "accessnotconfigured" in blob
            or "service_disabled" in blob
            or "youtube analytics api has not been used" in blob
        )

    def is_auth_problem(self):
        blob = f"{self.reason} {self.message}".lower()
        return self.status in (401, 403) and any(
            x in blob for x in ("invalid_grant", "insufficientpermissions", "unauthorized", "invalid credentials")
        )


class Amplifier:
    def __init__(self, base_url, key):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {key}"})

    def call(self, method, path, timeout=90, **kwargs):
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

    def token(self, amplifier_id):
        return self.call("GET", f"/api/channels/{amplifier_id}/token")


def extract_enable_url(message):
    m = re.search(r"https://console\.developers\.google\.com/apis/api/[^\s\"']+", message or "")
    return m.group(0) if m else None


def _parse_youtube_error(r):
    reason = ""
    message = r.text[:400]
    try:
        err = r.json().get("error", {})
        message = err.get("message") or message
        errors = err.get("errors") or []
        if errors:
            reason = errors[0].get("reason") or ""
    except Exception:
        pass
    return YouTubeError(r.status_code, reason, message, extract_enable_url(message))


def yt_get(token, path, params):
    r = requests.get(
        f"https://www.googleapis.com/youtube/v3/{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=60,
    )
    if not r.ok:
        raise _parse_youtube_error(r)
    return r.json()


def ya_get(token, params):
    r = requests.get(
        "https://youtubeanalytics.googleapis.com/v2/reports",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=60,
    )
    if not r.ok:
        raise _parse_youtube_error(r)
    return r.json()


# --------------------------------------------------------------------------- #
# Channel registry + sync
# --------------------------------------------------------------------------- #

def find_channel(con, needle):
    needle = (needle or "").strip()
    rows = [dict(r) for r in con.execute("SELECT * FROM channels ORDER BY title")]
    if not rows:
        raise SystemExit("No channels in the ledger yet. Run: python3 ceo.py sync")
    for c in rows:
        if needle.lower() == (c["title"] or "").lower():
            return c
    for c in rows:
        if needle.lower() == (c["youtube_id"] or "").lower() or needle == c["amplifier_id"]:
            return c
    for c in rows:
        if needle.lower() in (c["title"] or "").lower():
            return c
    raise SystemExit(f"Channel {needle!r} not found. Known: {[c['title'] for c in rows]}")


def ensure_channel(con, remote):
    yt_id = remote.get("youtubeChannelId")
    if not yt_id:
        return None
    row = con.execute("SELECT * FROM channels WHERE youtube_id=?", (yt_id,)).fetchone()
    if row:
        con.execute(
            "UPDATE channels SET amplifier_id=?, title=COALESCE(?, title), thumbnail=COALESCE(?, thumbnail) WHERE id=?",
            (remote.get("_id"), remote.get("title"), remote.get("thumbnail"), row["id"]),
        )
        return row["id"]
    skill = DEFAULT_SKILLS.get((remote.get("title") or "").strip().lower(), "")
    cur = con.execute(
        """INSERT INTO channels (youtube_id, amplifier_id, title, thumbnail, owner_skill, first_seen, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (yt_id, remote.get("_id"), remote.get("title"), remote.get("thumbnail"), skill, now_iso(),
         remote.get("status") or "connected"),
    )
    return cur.lastrowid


def auto_tier(video_count):
    if video_count is None:
        return "bet"
    if video_count < 10:
        return "bet"
    if video_count < 30:
        return "build"
    return "scale"


def upload_momentum(videos, min_age_days=7):
    """Newest 3 mature uploads vs the 3 before them, on views per day alive.

    This is the Data-API-only fallback for trend. It deliberately ignores
    uploads younger than a week: a video posted yesterday always looks like a
    bomb next to a video that has had 28 days to accumulate views, and calling
    that a decline is how a CEO talks themselves into a panic. It is still an
    upload-quality signal, not a traffic signal — it says whether the latest
    slate is beating the prior slate, not whether the channel grew this week.
    """
    eligible = []
    for v in videos:
        age = days_since(v.get("published_at"))
        if age is not None and age >= min_age_days:
            eligible.append((v, age))
    if len(eligible) < 6:
        return None
    rates = [(v.get("views") or 0) / max(age, 1) for v, age in eligible[:6]]
    newest = median(rates[:3])
    prior = median(rates[3:6])
    if not prior:
        return None
    return round(newest / prior, 2)


def fetch_analytics(token, yt_id, days):
    """YouTube Analytics API: daily channel series + per-video period totals.

    The token from Amplifier carries yt-analytics.readonly. If the Google Cloud
    project has the API disabled this raises YouTubeError with the enable URL.
    """
    end = date.today()
    start = end - timedelta(days=days - 1)
    daily_start = end - timedelta(days=max(days, 28) - 1)
    base = {
        "ids": f"channel=={yt_id}",
        "start-date": daily_start.isoformat(),
        "end-date": end.isoformat(),
    }
    data = ya_get(token, {
        **base,
        "metrics": "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost",
        "dimensions": "day",
        "sort": "day",
    })
    headers = [h.get("name") for h in data.get("columnHeaders", [])]
    daily = []
    for row in data.get("rows", []):
        rec = dict(zip(headers, row))
        daily.append({
            "day": rec.get("day"),
            "views": to_int(rec.get("views")) or 0,
            "watch_minutes": to_int(rec.get("estimatedMinutesWatched")) or 0,
            "subs_gained": to_int(rec.get("subscribersGained")) or 0,
            "subs_lost": to_int(rec.get("subscribersLost")) or 0,
        })

    period_rows = [d for d in daily if (d["day"] or "") >= start.isoformat()]
    period_views = sum(d["views"] for d in period_rows)
    period_watch = sum(d["watch_minutes"] for d in period_rows)
    period_subs_gained = sum(d["subs_gained"] for d in period_rows)
    period_subs_lost = sum(d["subs_lost"] for d in period_rows)
    avd = round(period_watch * 60 / period_views, 1) if period_views else None

    videos = {}
    video_error = None
    try:
        vdata = ya_get(token, {
            "ids": f"channel=={yt_id}",
            "start-date": start.isoformat(),
            "end-date": end.isoformat(),
            "metrics": "views,estimatedMinutesWatched,averageViewDuration,subscribersGained",
            "dimensions": "video",
            "sort": "-views",
            "maxResults": 50,
        })
        vheaders = [h.get("name") for h in vdata.get("columnHeaders", [])]
        for row in vdata.get("rows", []):
            rec = dict(zip(vheaders, row))
            vid = rec.get("video")
            if vid:
                videos[vid] = {
                    "period_views": to_int(rec.get("views")) or 0,
                    "period_watch_minutes": to_int(rec.get("estimatedMinutesWatched")) or 0,
                    "period_subs_gained": to_int(rec.get("subscribersGained")) or 0,
                }
    except YouTubeError as e:
        video_error = e.message

    return {
        "ok": True,
        "daily": daily,
        "period": {
            "views": period_views,
            "watch_minutes": period_watch,
            "subs_gained": period_subs_gained,
            "subs_lost": period_subs_lost,
            "avg_view_duration_sec": avd,
        },
        "videos": videos,
        "video_error": video_error,
    }


def sync_one(con, amp, ch, args, state):
    """Pull Data API + Analytics for one channel and write a snapshot."""
    out = {"channel": ch["title"], "channel_id": ch["id"], "ok": False}
    token = None
    try:
        token = amp.token(ch["amplifier_id"])["access_token"]
    except Exception as e:
        msg = str(e)
        status = "needs_reconnect" if "invalid_grant" in msg else ch["status"]
        con.execute(
            "UPDATE channels SET status=?, last_synced=?, analytics_error=? WHERE id=?",
            (status, now_iso(), msg[:500], ch["id"]),
        )
        out["error"] = msg
        return out

    try:
        data = yt_get(token, "channels", {
            "part": "snippet,statistics,contentDetails,brandingSettings",
            "id": ch["youtube_id"],
        })
        items = data.get("items") or []
        if not items:
            out["error"] = "YouTube returned no channel for this id"
            return out
        item = items[0]
        snippet = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        branding = (item.get("brandingSettings") or {}).get("channel") or {}
        uploads_playlist = ((item.get("contentDetails") or {}).get("relatedPlaylists") or {}).get("uploads")

        subs = to_int(stats.get("subscriberCount"))
        total_views = to_int(stats.get("viewCount"))
        video_count = to_int(stats.get("videoCount"))

        video_ids = []
        page_token = None
        while uploads_playlist and len(video_ids) < args.max_videos:
            params = {
                "part": "snippet,contentDetails",
                "playlistId": uploads_playlist,
                "maxResults": min(50, args.max_videos - len(video_ids)),
            }
            if page_token:
                params["pageToken"] = page_token
            page = yt_get(token, "playlistItems", params)
            for it in page.get("items", []):
                vid = ((it.get("contentDetails") or {}).get("videoId"))
                if vid:
                    video_ids.append(vid)
            page_token = page.get("nextPageToken")
            if not page_token:
                break

        video_objs = []
        for batch in chunked(video_ids, 50):
            detail = yt_get(token, "videos", {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(batch),
            })
            for v in detail.get("items", []):
                sn = v.get("snippet") or {}
                st = v.get("statistics") or {}
                cd = v.get("contentDetails") or {}
                video_objs.append({
                    "youtube_video_id": v.get("id"),
                    "title": sn.get("title") or "Untitled",
                    "published_at": sn.get("publishedAt"),
                    "duration_sec": parse_duration(cd.get("duration")),
                    "views": to_int(st.get("viewCount")) or 0,
                    "likes": to_int(st.get("likeCount")) or 0,
                    "comments": to_int(st.get("commentCount")) or 0,
                })
        video_objs.sort(key=lambda v: v.get("published_at") or "", reverse=True)

        stamp = now_iso()
        con.execute("UPDATE videos SET period_views=NULL, period_watch_minutes=NULL, period_subs_gained=NULL WHERE channel_id=?", (ch["id"],))
        for v in video_objs:
            con.execute(
                """INSERT INTO videos (channel_id, youtube_video_id, title, published_at, duration_sec,
                                       views, likes, comments, first_seen, last_seen)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(channel_id, youtube_video_id) DO UPDATE SET
                     title=excluded.title, published_at=excluded.published_at,
                     duration_sec=excluded.duration_sec, views=excluded.views,
                     likes=excluded.likes, comments=excluded.comments, last_seen=excluded.last_seen""",
                (ch["id"], v["youtube_video_id"], v["title"], v["published_at"], v["duration_sec"],
                 v["views"], v["likes"], v["comments"], stamp, stamp),
            )

        analytics = None
        analytics_status = "skipped" if args.no_analytics else "not_checked"
        analytics_error = None
        if not args.no_analytics and not state["analytics_disabled"]:
            try:
                analytics = fetch_analytics(token, ch["youtube_id"], args.days)
                analytics_status = "ok"
                for vid, m in analytics["videos"].items():
                    con.execute(
                        """UPDATE videos SET period_views=?, period_watch_minutes=?, period_subs_gained=?
                           WHERE channel_id=? AND youtube_video_id=?""",
                        (m["period_views"], m["period_watch_minutes"], m["period_subs_gained"], ch["id"], vid),
                    )
            except YouTubeError as e:
                analytics_error = e.message
                if e.is_analytics_disabled():
                    state["analytics_disabled"] = True
                    state["analytics_error"] = e.message
                    state["analytics_url"] = e.enable_url
                    analytics_status = "disabled"
                else:
                    analytics_status = "error"
        elif state["analytics_disabled"]:
            analytics_status = "disabled"
            analytics_error = state.get("analytics_error")

        # Daily series (only when the Analytics API answered).
        if analytics:
            for d in analytics["daily"]:
                con.execute(
                    """INSERT INTO daily (channel_id, day, views, watch_minutes, subs_gained, subs_lost)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(channel_id, day) DO UPDATE SET
                         views=excluded.views, watch_minutes=excluded.watch_minutes,
                         subs_gained=excluded.subs_gained, subs_lost=excluded.subs_lost""",
                    (ch["id"], d["day"], d["views"], d["watch_minutes"], d["subs_gained"], d["subs_lost"]),
                )

        rows = [dict(r) for r in con.execute(
            "SELECT * FROM videos WHERE channel_id=? ORDER BY published_at DESC", (ch["id"],)
        )]
        start = (date.today() - timedelta(days=args.days - 1)).isoformat()
        in_period = [v for v in rows if (v.get("published_at") or "")[:10] >= start]
        uploads_in_period = len(in_period)
        new_video_views = sum(v.get("views") or 0 for v in in_period)
        typical_views = median([v.get("views") or 0 for v in rows[:10]])
        typical_views = int(typical_views) if typical_views is not None else None
        momentum = upload_momentum(rows)

        previous = con.execute(
            "SELECT subs, taken_at FROM snapshots WHERE channel_id=? ORDER BY taken_at DESC LIMIT 1",
            (ch["id"],),
        ).fetchone()
        subs_delta = None
        if previous and previous["subs"] is not None and subs is not None:
            subs_delta = subs - previous["subs"]

        period = (analytics or {}).get("period") or {}
        con.execute(
            """INSERT INTO snapshots (
                 channel_id, taken_at, range_days, subs, total_views, video_count,
                 period_views, period_watch_minutes, period_subs_gained, period_subs_lost,
                 avg_view_duration_sec, uploads_in_period, new_video_views, typical_views,
                 momentum, subs_delta, analytics_ok, data_source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ch["id"], stamp, args.days, subs, total_views, video_count,
             period.get("views"), period.get("watch_minutes"), period.get("subs_gained"),
             period.get("subs_lost"), period.get("avg_view_duration_sec"),
             uploads_in_period, new_video_views, typical_views, momentum, subs_delta,
             1 if analytics else 0,
             "data+analytics" if analytics else "data-api"),
        )

        tier = ch["tier"] if ch["tier_locked"] else auto_tier(video_count)
        new_status = "paused" if ch.get("status") == "paused" else "connected"
        con.execute(
            """UPDATE channels SET title=?, handle=?, description=?, thumbnail=?, status=?,
                 last_synced=?, analytics_status=?, analytics_error=?, tier=?
               WHERE id=?""",
            (snippet.get("title") or ch["title"], snippet.get("customUrl"), branding.get("description") or ch["description"],
             (snippet.get("thumbnails") or {}).get("default", {}).get("url") or ch["thumbnail"],
             new_status, stamp, analytics_status, (analytics_error or "")[:1000], tier, ch["id"]),
        )

        latest = rows[0] if rows else None
        out.update({
            "ok": True,
            "subs": subs,
            "total_views": total_views,
            "video_count": video_count,
            "uploads_in_period": uploads_in_period,
            "new_video_views": new_video_views,
            "typical_views": typical_views,
            "momentum": momentum,
            "subs_delta": subs_delta,
            "days_since_upload": days_since((latest or {}).get("published_at")),
            "analytics_status": analytics_status,
        })
        con.commit()
        return out
    except YouTubeError as e:
        status = "needs_reconnect" if e.is_auth_problem() else ch["status"]
        con.execute(
            "UPDATE channels SET status=?, last_synced=?, analytics_error=? WHERE id=?",
            (status, now_iso(), str(e)[:1000], ch["id"]),
        )
        out["error"] = str(e)
        return out
    except Exception as e:
        out["error"] = str(e)
        return out


def add_task_once(con, channel_id, title, due):
    existing = con.execute(
        "SELECT id FROM tasks WHERE channel_id=? AND title=? AND status='open'",
        (channel_id, title),
    ).fetchone()
    if existing:
        return existing["id"]
    cur = con.execute(
        "INSERT INTO tasks (channel_id, title, owner, due, status, created_at) VALUES (?, ?, 'CEO', ?, 'open', ?)",
        (channel_id, title, due, now_iso()),
    )
    return cur.lastrowid


def ensure_playbook(con, ch, force=False):
    path = ceo_home() / "channels" / f"{slugify(ch['title'])}.md"
    if path.exists() and not force:
        return path, False
    template = Path(__file__).resolve().parent.parent / "templates" / "channel-playbook.md"
    text = template.read_text(encoding="utf-8")
    replacements = {
        "{{CHANNEL}}": ch["title"] or "",
        "{{YOUTUBE_ID}}": ch["youtube_id"] or "",
        "{{AMPLIFIER_ID}}": ch["amplifier_id"] or "",
        "{{SKILL}}": ch["owner_skill"] or "none yet",
        "{{DATE}}": today_iso(),
        "{{TIER}}": ch["tier"] or "bet",
        "{{CADENCE}}": f"{ch['cadence_per_week']:g}",
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path, True


def cmd_sync(args):
    con = connect()
    amp = Amplifier(args.api_url, read_key(args.api_key))
    remote = amp.channels()
    if args.channel:
        needle = args.channel.lower()
        remote = [c for c in remote if needle in (c.get("title") or "").lower() or needle == c.get("youtubeChannelId", "").lower()]
        if not remote:
            raise SystemExit(f"No connected channel matches {args.channel!r}")
    if not remote:
        raise SystemExit("Amplifier has no connected channels. Connect one in the dashboard first.")

    known_before = {r["youtube_id"] for r in con.execute("SELECT youtube_id FROM channels")}
    for c in remote:
        ensure_channel(con, c)
    con.commit()

    newly_connected = [c for c in remote if c.get("youtubeChannelId") not in known_before]

    stale = []
    if not args.channel:
        remote_ids = {c.get("youtubeChannelId") for c in remote}
        for row in con.execute("SELECT id, youtube_id, title, status FROM channels").fetchall():
            if row["youtube_id"] not in remote_ids and row["status"] != "disconnected":
                con.execute("UPDATE channels SET status='disconnected' WHERE id=?", (row["id"],))
                stale.append(row["title"])
        if stale:
            con.commit()

    state = {"analytics_disabled": False, "analytics_error": None, "analytics_url": None}
    started = now_iso()
    results = []
    for c in remote:
        row = con.execute("SELECT * FROM channels WHERE youtube_id=?", (c.get("youtubeChannelId"),)).fetchone()
        if not row:
            continue
        results.append(sync_one(con, amp, dict(row), args, state))

    by_channel = {r.get("channel_id"): r for r in results}
    for c in newly_connected:
        ch = con.execute("SELECT * FROM channels WHERE youtube_id=?", (c.get("youtubeChannelId"),)).fetchone()
        if not ch:
            continue
        path, made = ensure_playbook(con, dict(ch))
        video_count = (by_channel.get(ch["id"]) or {}).get("video_count") or 0
        if not made and video_count > 0:
            continue
        if video_count == 0:
            task = f"Onboard {ch['title']}: fill {path.name} + write the first 3 titles"
        else:
            task = f"Write the {ch['title']} playbook and lock packaging from the existing catalogue"
        add_task_once(con, ch["id"], task, (date.today() + timedelta(days=7)).isoformat())
    con.commit()

    ok = sum(1 for r in results if r.get("ok"))
    failed = len(results) - ok
    con.execute(
        "INSERT INTO sync_runs (started_at, finished_at, ok, failed, detail) VALUES (?, ?, ?, ?, ?)",
        (started, now_iso(), ok, failed, json.dumps(results, ensure_ascii=False)),
    )
    con.commit()

    if args.json:
        print(json.dumps({
            "synced": ok, "failed": failed, "channels": results,
            "newlyConnected": [c.get("title") for c in newly_connected],
            "disconnected": stale,
            "analytics": {
                "status": "disabled" if state["analytics_disabled"] else "ok",
                "error": state.get("analytics_error"),
                "enable_url": state.get("analytics_url"),
            },
        }, indent=2, ensure_ascii=False))
        return

    print(f"Synced {ok}/{len(results)} channels into {db_path()}")
    if newly_connected:
        print(f"  + new channels discovered: {', '.join(c.get('title') or '?' for c in newly_connected)}")
        print("    Playbooks checked and onboarding tasks added where needed.")
    if stale:
        print(f"  ! no longer connected in Amplifier: {', '.join(stale)}")
        print("    Marked disconnected in the ledger; reconnect or remove them deliberately.")
    for r in results:
        if not r.get("ok"):
            print(f"  ✗ {r['channel']}: {r.get('error', 'unknown error')}")
            continue
        print(
            f"  ✓ {r['channel']}: {fmt_int(r.get('subs'))} subs · "
            f"{fmt_int(r.get('total_views'))} lifetime views · "
            f"{r.get('uploads_in_period')} uploads/{args.days}d · "
            f"typical {fmt_int(r.get('typical_views'))} · "
            f"momentum {fmt_momentum(r.get('momentum'))} · "
            f"last upload {r.get('days_since_upload')}d ago"
        )
    if state["analytics_disabled"]:
        url = state.get("analytics_url") or "https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com"
        print("\nAnalytics API is OFF for this Google Cloud project.")
        print("Watch time, true 28-day views, subs gained and retention stay unavailable until it is enabled:")
        print(f"  {url}")
        print("Data API numbers above are still real; they are just lifetime totals, not period traffic.")
    print(f"\nNext: python3 {Path(__file__).name} report")


# --------------------------------------------------------------------------- #
# Verdicts, reads, and the report
# --------------------------------------------------------------------------- #

def verdict_for(ch, snap, days):
    cadence = ch.get("cadence_per_week") or 1
    target_gap = 7.0 / max(cadence, 0.25)
    if ch.get("status") == "disconnected":
        return "DISCONNECTED", (
            "This channel is in the ledger but no longer connected in Amplifier. Reconnect it, "
            "or remove it from the portfolio on purpose."
        )
    if ch.get("status") == "paused":
        return "PAUSED", (
            "Manually paused. It stays out of the slate until the owner unpauses it; do not spend "
            "attention on it just because it is in the list."
        )
    if ch.get("status") not in ("connected", None):
        return "FIX AUTH", "Reconnect the channel in Amplifier. Nothing else matters until the token works."
    if snap is None or (snap.get("video_count") or 0) == 0:
        return "ONBOARD", (
            "No uploads recorded. Fill the playbook and write the first three titles before spending "
            "a production run on this channel."
        )
    if days is None or days > 45:
        return "PARK", (
            "No upload in " + (f"{days} days" if days is not None else "the recorded window") +
            ". Commission a restart video this week or formally park the channel and move its hours to a winner."
        )
    if days > target_gap + 3:
        return "SHIP", (
            f"Cadence gap: {days} days since the last upload, target is every {target_gap:.0f} days. "
            "Ship the next commissioned video before changing strategy."
        )
    momentum = (snap or {}).get("momentum")
    if momentum is not None and momentum <= 0.85:
        return "FIX", (
            f"Momentum is {momentum:.2f}× the prior slate. Fix packaging first — title and thumbnail — "
            "before paying for another full production run."
        )
    if momentum is not None and momentum >= 1.15:
        return "SCALE", (
            f"Momentum is {momentum:.2f}× the prior slate. Double down on the pillar that produced it; "
            "add a second weekly slot only if production can hold quality."
        )
    return "HOLD", "Within the normal range. Keep cadence and change one variable in the next video."


def channel_read(ch, snap, videos, days):
    bits = []
    if not snap:
        return "No snapshot yet. Run sync before making a call on this channel."
    if snap.get("analytics_ok") == 0:
        bits.append("Watch time and retention are missing because the Analytics API is off.")
    latest = videos[0] if videos else None
    typical = snap.get("typical_views")
    latest_age = days_since(latest.get("published_at")) if latest else None
    if latest and typical and latest_age is not None and latest_age >= 7:
        ratio = (latest.get("views") or 0) / typical if typical else 0
        if ratio < 0.6:
            bits.append(f"The latest video is at {ratio:.0%} of the channel's typical — a packaging or topic miss, not a production problem.")
        elif ratio > 1.5:
            bits.append(f"The latest video is {ratio:.1f}× typical — the angle is working; make the next two sequels before the audience forgets.")
    elif latest and latest_age is not None and latest_age < 7:
        when = "today" if latest_age == 0 else f"{latest_age} day{'s' if latest_age != 1 else ''} ago"
        bits.append(f"The latest upload is from {when}; judge it on day 7, not today.")
    momentum = snap.get("momentum")
    if momentum is not None:
        if momentum >= 1.15:
            bits.append(f"The newest three uploads are beating the previous three by {momentum:.2f}×.")
        elif momentum <= 0.85:
            bits.append(f"The newest three uploads are at {momentum:.2f}× the previous three — the slate is weakening.")
    subs = snap.get("subs") or 0
    views = snap.get("total_views") or 0
    if views >= 500:
        per_1k = subs / (views / 1000)
        if per_1k < 2:
            bits.append(f"Only ~{per_1k:.1f} subs per 1,000 lifetime views — the videos reach but do not convert. Fix the promise and the end screen.")
        elif per_1k >= 5:
            bits.append(f"~{per_1k:.1f} subs per 1,000 views — conversion is healthy; more reach is the constraint.")
    if snap.get("uploads_in_period", 0) < 3:
        bits.append("The sample is thin; judge the next three videos on packaging and retention, not on subs.")
    if days is None:
        bits.append("No upload is recorded yet.")
    if not bits:
        bits.append("No strong signal either way. Keep the cadence and test one variable.")
    return " ".join(bits)


def latest_snapshot(con, channel_id, range_days):
    row = con.execute(
        """SELECT * FROM snapshots WHERE channel_id=?
           ORDER BY (range_days=?) DESC, taken_at DESC LIMIT 1""",
        (channel_id, range_days),
    ).fetchone()
    return dict(row) if row else None


def build_report(con, args):
    channels = [dict(r) for r in con.execute("SELECT * FROM channels ORDER BY title")]
    if args.channel:
        needle = args.channel.lower()
        channels = [c for c in channels if needle in (c["title"] or "").lower()]
        if not channels:
            raise SystemExit(f"No channel matches {args.channel!r}")
    if not channels:
        raise SystemExit("No channels in the ledger. Run: python3 ceo.py sync")

    cards = []
    for ch in channels:
        snap = latest_snapshot(con, ch["id"], args.days)
        videos = [dict(r) for r in con.execute(
            "SELECT * FROM videos WHERE channel_id=? ORDER BY published_at DESC LIMIT 50",
            (ch["id"],),
        )]
        latest = videos[0] if videos else None
        days = days_since((latest or {}).get("published_at")) if latest else None
        verdict, next_move = verdict_for(ch, snap, days)
        typical = (snap or {}).get("typical_views")
        latest_views = (latest or {}).get("views")
        latest_ratio = (
            round(latest_views / typical, 2)
            if latest_views is not None and typical and days is not None and days >= 7
            else None
        )
        ranked = [v for v in videos[:10] if (v.get("views") or 0) > 0]
        best = max(ranked, key=lambda v: v.get("views") or 0) if ranked else None
        worst = min(ranked, key=lambda v: v.get("views") or 0) if ranked else None
        cards.append({
            "channel": ch,
            "snapshot": snap,
            "latest": latest,
            "days_since_upload": days,
            "verdict": verdict,
            "next_move": next_move,
            "read": channel_read(ch, snap, videos, days),
            "latest_ratio": latest_ratio,
            "best": best,
            "worst": worst,
            "playbook": str(ceo_home() / "channels" / f"{slugify(ch['title'])}.md"),
        })

    decisions_due = [dict(r) for r in con.execute(
        """SELECT d.*, c.title AS channel_title FROM decisions d
           LEFT JOIN channels c ON c.id=d.channel_id
           WHERE d.status='open' AND (d.review_on IS NULL OR d.review_on <= ?)
           ORDER BY d.review_on, d.id""",
        (today_iso(),),
    )]
    tasks = [dict(r) for r in con.execute(
        """SELECT t.*, c.title AS channel_title FROM tasks t
           LEFT JOIN channels c ON c.id=t.channel_id
           WHERE t.status='open' ORDER BY (t.due IS NULL), t.due, t.id"""
    )]
    slate = [dict(r) for r in con.execute(
        """SELECT s.*, c.title AS channel_title FROM slate s
           LEFT JOIN channels c ON c.id=s.channel_id
           WHERE s.status != 'dropped' AND s.publish_on >= ? AND s.publish_on <= ?
           ORDER BY s.publish_on, s.id""",
        (today_iso(), (date.today() + timedelta(days=14)).isoformat()),
    )]
    analytics_errors = [c["analytics_error"] for c in channels if c.get("analytics_error")]
    enable_url = next((extract_enable_url(e) for e in analytics_errors if extract_enable_url(e)), None)
    coverage = {
        "channels": len(cards),
        "playbooks": sum(1 for c in cards if Path(c["playbook"]).exists()),
        "skills": sum(1 for c in cards if c["channel"].get("owner_skill")),
        "unplaybooked": [c["channel"]["title"] for c in cards if not Path(c["playbook"]).exists()],
        "unskilled": [c["channel"]["title"] for c in cards if not c["channel"].get("owner_skill")],
    }
    return {
        "generated_at": now_iso(),
        "range_days": args.days,
        "cards": cards,
        "coverage": coverage,
        "decisions_due": decisions_due,
        "tasks": tasks,
        "slate": slate,
        "analytics": {
            "ok": any((c["snapshot"] or {}).get("analytics_ok") for c in cards),
            "enable_url": enable_url,
            "error": analytics_errors[0] if analytics_errors else None,
        },
    }


def render_report(data):
    cards = data["cards"]
    any_analytics = data["analytics"]["ok"]
    lines = []
    lines.append(f"# Amplifier portfolio review — {date.today().isoformat()}")
    lines.append("")
    lines.append(f"Last {data['range_days']} days · {len(cards)} channels · ledger: `{db_path()}`")
    cov = data.get("coverage") or {}
    if cov:
        gap_bits = []
        if cov.get("unplaybooked"):
            gap_bits.append(f"no playbook: {', '.join(cov['unplaybooked'])}")
        if cov.get("unskilled"):
            gap_bits.append(f"no builder skill: {', '.join(cov['unskilled'])}")
        lines.append(
            f"Coverage: {cov.get('playbooks', 0)}/{cov.get('channels', 0)} playbooks · "
            f"{cov.get('skills', 0)}/{cov.get('channels', 0)} builder skills"
            + ((" · " + "; ".join(gap_bits)) if gap_bits else "")
        )
    lines.append("")
    if not any_analytics:
        url = data["analytics"].get("enable_url") or "https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com"
        lines.append("> **Data caveat:** the YouTube Analytics API is disabled for this Google Cloud project, so watch time, true period views and retention are missing. Lifetime totals and upload-level views below are real Data API numbers. Enable it here: " + url)
        lines.append("")

    lines.append("## Scorecard")
    lines.append("")
    lines.append(f"| Channel | Tier | Subs | {data['range_days']}d views | Watch h | Subs Δ | Uploads | Typical | Momentum | Last upload | Verdict |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    totals = {"subs": 0, "views": 0, "period_views": 0, "watch": 0, "uploads": 0}
    for card in cards:
        ch, snap = card["channel"], card["snapshot"] or {}
        period_views = snap.get("period_views")
        watch_h = round((snap.get("period_watch_minutes") or 0) / 60, 1) if period_views is not None else None
        lines.append(
            f"| **{ch['title']}** | {ch['tier']} | {fmt_int(snap.get('subs'))} | "
            f"{fmt_int(period_views)} | {fmt_int(watch_h)} | {fmt_signed(snap.get('subs_delta'))} | "
            f"{fmt_int(snap.get('uploads_in_period'))} | {fmt_int(snap.get('typical_views'))} | "
            f"{fmt_momentum(snap.get('momentum'))} | "
            f"{str(card['days_since_upload']) + 'd' if card['days_since_upload'] is not None else '—'} | "
            f"**{card['verdict']}** |"
        )
        for key, value in (("subs", snap.get("subs")), ("views", snap.get("total_views")),
                           ("period_views", period_views), ("watch", watch_h),
                           ("uploads", snap.get("uploads_in_period"))):
            if value:
                totals[key] += value
    lines.append(
        f"| **Portfolio** | — | {fmt_int(totals['subs'])} | {fmt_int(totals['period_views']) if any_analytics else '—'} | "
        f"{fmt_int(totals['watch']) if any_analytics else '—'} | — | {fmt_int(totals['uploads'])} | — | — | — | — |"
    )
    lines.append("")

    lines.append("## What changed")
    lines.append("")
    bullets = []
    risers = [c for c in cards if (c["snapshot"] or {}).get("momentum") and c["snapshot"]["momentum"] >= 1.15]
    slippers = [c for c in cards if (c["snapshot"] or {}).get("momentum") and c["snapshot"]["momentum"] <= 0.85]
    gaps = [c for c in cards if c["verdict"] == "SHIP"]
    auths = [c for c in cards if c["verdict"] == "FIX AUTH"]
    parks = [c for c in cards if c["verdict"] == "PARK"]
    onboards = [c for c in cards if c["verdict"] == "ONBOARD"]
    disconnected = [c for c in cards if c["verdict"] == "DISCONNECTED"]
    paused = [c for c in cards if c["verdict"] == "PAUSED"]
    for c in disconnected:
        bullets.append(f"**Disconnected:** {c['channel']['title']} — in the ledger, no longer connected in Amplifier. Reconnect or remove it on purpose.")
    for c in paused:
        bullets.append(f"**Paused:** {c['channel']['title']} — deliberately off the slate; not a performance problem.")
    for c in onboards:
        bullets.append(f"**Needs onboarding:** {c['channel']['title']} — no uploads yet; playbook and first three titles come before production.")
    for c in sorted(risers, key=lambda x: -(x["snapshot"]["momentum"] or 0)):
        bullets.append(f"**Rising:** {c['channel']['title']} — newest three uploads at {c['snapshot']['momentum']:.2f}× the prior three.")
    for c in sorted(slippers, key=lambda x: x["snapshot"]["momentum"] or 0):
        bullets.append(f"**Slipping:** {c['channel']['title']} — newest three uploads at {c['snapshot']['momentum']:.2f}× the prior three.")
    for c in gaps:
        bullets.append(f"**Behind cadence:** {c['channel']['title']} — {c['days_since_upload']} days since the last upload.")
    for c in auths:
        bullets.append(f"**Auth broken:** {c['channel']['title']} — reconnect it before planning anything.")
    for c in parks:
        bullets.append(f"**Parked risk:** {c['channel']['title']} — {c['days_since_upload'] if c['days_since_upload'] is not None else '45+'} days without an upload.")
    cov_gaps = []
    if (data.get("coverage") or {}).get("unplaybooked"):
        cov_gaps.append("no playbook: " + ", ".join(data["coverage"]["unplaybooked"]))
    if (data.get("coverage") or {}).get("unskilled"):
        cov_gaps.append("no builder skill: " + ", ".join(data["coverage"]["unskilled"]))
    if cov_gaps:
        bullets.append("**Portfolio gaps:** " + "; ".join(cov_gaps) + ".")
    if not bullets:
        bullets.append("Nothing is screaming. The portfolio is inside its normal range; keep the cadence and make one deliberate bet.")
    if not any((c["snapshot"] or {}).get("subs_delta") for c in cards):
        bullets.append("First comparable snapshot: subscriber and view deltas start after the next sync.")
    if not any_analytics:
        bullets.append("Analytics API still off: no watch time, retention or true period traffic. Treat reach reads as upload-level, not channel-level.")
    lines.extend(f"- {b}" for b in bullets)
    lines.append("")

    lines.append("## Channel notes")
    lines.append("")
    for card in cards:
        ch, snap = card["channel"], card["snapshot"] or {}
        latest = card["latest"]
        lines.append(f"### {ch['title']} — {card['verdict']}")
        lines.append(
            f"`{ch['tier']}` · {ch['cadence_per_week']:g}/week target · "
            f"last upload {card['days_since_upload']}d ago · "
            f"skill: `{ch['owner_skill'] or 'none yet'}`"
        )
        lines.append("")
        lines.append(
            f"- **Numbers:** {fmt_int(snap.get('subs'))} subs · {fmt_int(snap.get('total_views'))} lifetime views · "
            f"{fmt_int(snap.get('video_count'))} {'video' if snap.get('video_count') == 1 else 'videos'} · typical {fmt_int(snap.get('typical_views'))} · "
            f"momentum {fmt_momentum(snap.get('momentum'))}"
        )
        if latest:
            ratio = f" ({card['latest_ratio']:.2f}× typical)" if card["latest_ratio"] is not None else ""
            lines.append(f"- **Latest:** {shorten(latest.get('title'), 96)} — {fmt_int(latest.get('views'))} views{ratio}")
        if card["best"]:
            lines.append(f"- **Best recent:** {shorten(card['best'].get('title'), 96)} — {fmt_int(card['best'].get('views'))} views")
        if card["worst"] and card["worst"].get("youtube_video_id") != (card["best"] or {}).get("youtube_video_id"):
            lines.append(f"- **Weakest recent:** {shorten(card['worst'].get('title'), 96)} — {fmt_int(card['worst'].get('views'))} views")
        lines.append(f"- **Read:** {card['read']}")
        lines.append(f"- **Next move:** {card['next_move']}")
        if ch.get("notes"):
            lines.append(f"- **Playbook note:** {ch['notes']}")
        lines.append("")

    lines.append("## Decisions due")
    lines.append("")
    if data["decisions_due"]:
        lines.append("| # | Channel | Decision | Review on | Why |")
        lines.append("|---|---|---|---|---|")
        for d in data["decisions_due"]:
            lines.append(
                f"| {d['id']} | {d.get('channel_title') or 'Portfolio'} | {shorten(d['decision'], 80)} | "
                f"{d.get('review_on') or '—'} | {shorten(d['rationale'], 100)} |"
            )
    else:
        lines.append("No decisions are due for review.")
    lines.append("")

    lines.append("## Open tasks")
    lines.append("")
    if data["tasks"]:
        lines.append("| # | Channel | Task | Owner | Due |")
        lines.append("|---|---|---|---|---|")
        for t in data["tasks"]:
            due = t.get("due") or "—"
            overdue = " **(overdue)**" if t.get("due") and t["due"] < today_iso() else ""
            lines.append(f"| {t['id']} | {t.get('channel_title') or 'Portfolio'} | {shorten(t['title'], 80)} | {t.get('owner') or 'CEO'} | {due}{overdue} |")
    else:
        lines.append("No open tasks.")
    lines.append("")

    lines.append("## Next 14 days")
    lines.append("")
    if data["slate"]:
        lines.append("| Date | Channel | Title | Format | Status |")
        lines.append("|---|---|---|---|---|")
        for s in data["slate"]:
            lines.append(f"| {s['publish_on']} | {s.get('channel_title') or '—'} | {shorten(s['title'], 80)} | {s.get('format') or '—'} | {s.get('status')} |")
    else:
        lines.append("No slate yet. A portfolio without a slate is just a dashboard.")
    lines.append("")

    lines.append("---")
    lines.append("Generated by `amplifier-yt-skill/scripts/ceo.py`. The model writes the executive brief and owner asks on top of this data pack.")
    return "\n".join(lines)


def cmd_report(args):
    con = connect()
    data = build_report(con, args)
    if args.json:
        payload = {
            "generated_at": data["generated_at"],
            "range_days": data["range_days"],
            "coverage": data.get("coverage"),
            "analytics": data["analytics"],
            "channels": [
                {
                    "title": c["channel"]["title"],
                    "youtube_id": c["channel"]["youtube_id"],
                    "tier": c["channel"]["tier"],
                    "status": c["channel"]["status"],
                    "owner_skill": c["channel"]["owner_skill"],
                    "playbook": c["playbook"],
                    "snapshot": c["snapshot"],
                    "latest": c["latest"],
                    "days_since_upload": c["days_since_upload"],
                    "verdict": c["verdict"],
                    "read": c["read"],
                    "next_move": c["next_move"],
                } for c in data["cards"]
            ],
            "decisions_due": data["decisions_due"],
            "tasks": data["tasks"],
            "slate": data["slate"],
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        text = render_report(data)
    if args.out:
        path = Path(args.out).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {path}")
        if not args.json:
            print("\n" + text.split("## Scorecard")[1].split("## What changed")[0].strip()[:1600])
    else:
        print(text)


# --------------------------------------------------------------------------- #
# Ledger commands
# --------------------------------------------------------------------------- #

def cmd_channels(args):
    con = connect()
    rows = [dict(r) for r in con.execute("SELECT * FROM channels ORDER BY title")]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("No channels yet. Run: python3 ceo.py sync")
        return
    print(f"{'CHANNEL':28} {'TIER':7} {'CADENCE':8} {'SUBS':>6} {'VIDEOS':>7} {'STATUS':16} {'SKILL':32}")
    for c in rows:
        snap = latest_snapshot(con, c["id"], 28) or {}
        print(
            f"{shorten(c['title'], 27):28} {c['tier']:7} {c['cadence_per_week']:>5g}/w "
            f"{fmt_int(snap.get('subs')):>6} {fmt_int(snap.get('video_count')):>7} "
            f"{c['status'][:15]:16} {(c['owner_skill'] or '—')[:31]:32}"
        )
    print(f"\nLedger: {db_path()}")


def cmd_channel_set(args):
    con = connect()
    ch = find_channel(con, args.channel)
    fields = []
    values = []
    if args.tier:
        fields.extend(["tier", "tier_locked"])
        values.extend([args.tier, 1])
    if args.auto_tier:
        snap = latest_snapshot(con, ch["id"], 28) or {}
        fields.extend(["tier", "tier_locked"])
        values.extend([auto_tier(snap.get("video_count")), 0])
    if args.cadence is not None:
        fields.append("cadence_per_week")
        values.append(args.cadence)
    if args.pillar is not None:
        fields.append("pillar")
        values.append(args.pillar)
    if args.skill is not None:
        fields.append("owner_skill")
        values.append(args.skill)
    if args.status:
        fields.append("status")
        values.append(args.status)
    if args.notes is not None:
        fields.append("notes")
        values.append(args.notes)
    if not fields:
        raise SystemExit("Nothing to change. Pass --tier, --cadence, --pillar, --skill, --status or --notes.")
    values.append(ch["id"])
    con.execute(f"UPDATE channels SET {', '.join(f'{f}=?' for f in fields)} WHERE id=?", values)
    con.commit()
    updated = dict(con.execute("SELECT * FROM channels WHERE id=?", (ch["id"],)).fetchone())
    print(json.dumps(updated, indent=2, ensure_ascii=False))


def cmd_log(args):
    con = connect()
    channel_id = None
    if args.channel:
        channel_id = find_channel(con, args.channel)["id"]
    review_on = args.review_on or (date.today() + timedelta(days=14)).isoformat()
    cur = con.execute(
        "INSERT INTO decisions (channel_id, made_at, decision, rationale, review_on, status) VALUES (?, ?, ?, ?, ?, 'open')",
        (channel_id, now_iso(), args.decision, args.why, review_on),
    )
    con.commit()
    print(f"Logged decision #{cur.lastrowid} for review on {review_on}.")


def cmd_outcome(args):
    con = connect()
    con.execute(
        "UPDATE decisions SET status='reviewed', outcome=? WHERE id=?",
        (args.outcome, args.id),
    )
    con.commit()
    print(f"Decision #{args.id} closed.")


def cmd_task_add(args):
    con = connect()
    channel_id = find_channel(con, args.channel)["id"] if args.channel else None
    cur = con.execute(
        "INSERT INTO tasks (channel_id, title, owner, due, status, created_at) VALUES (?, ?, ?, ?, 'open', ?)",
        (channel_id, args.title, args.owner or "CEO", args.due, now_iso()),
    )
    con.commit()
    print(f"Added task #{cur.lastrowid}: {args.title}")


def cmd_task_done(args):
    con = connect()
    con.execute("UPDATE tasks SET status='done', done_at=? WHERE id=?", (now_iso(), args.id))
    con.commit()
    print(f"Task #{args.id} done.")


def cmd_tasks(args):
    con = connect()
    where = "WHERE t.status='open'" if not args.all else ""
    rows = [dict(r) for r in con.execute(
        f"""SELECT t.*, c.title AS channel_title FROM tasks t
            LEFT JOIN channels c ON c.id=t.channel_id {where}
            ORDER BY (t.due IS NULL), t.due, t.id"""
    )]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("No tasks.")
        return
    for t in rows:
        due = t.get("due") or "no due date"
        flag = " OVERDUE" if t.get("due") and t["due"] < today_iso() and t["status"] == "open" else ""
        print(f"#{t['id']:>3}  [{t['status']}]  {t.get('channel_title') or 'Portfolio':22}  {t['title']}  ({due}){flag}")


def cmd_slate_add(args):
    con = connect()
    ch = find_channel(con, args.channel)
    cur = con.execute(
        "INSERT INTO slate (channel_id, publish_on, title, format, status, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ch["id"], args.publish_on, args.title, args.format, args.status, args.notes, now_iso()),
    )
    con.commit()
    print(f"Slated #{cur.lastrowid}: {ch['title']} · {args.publish_on} · {args.title}")


def cmd_slate(args):
    con = connect()
    rows = [dict(r) for r in con.execute(
        """SELECT s.*, c.title AS channel_title FROM slate s
           LEFT JOIN channels c ON c.id=s.channel_id
           WHERE s.status != 'dropped' ORDER BY s.publish_on, s.id"""
    )]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("No slate. Add one with slate-add.")
        return
    for s in rows:
        marker = "→" if s["publish_on"] >= today_iso() else "·"
        print(f"{marker} #{s['id']:>3}  {s['publish_on']}  {s.get('channel_title') or '—':22}  [{s['status']:9}]  {s['title']}")


def cmd_slate_status(args):
    con = connect()
    con.execute("UPDATE slate SET status=? WHERE id=?", (args.status, args.id))
    con.commit()
    print(f"Slate #{args.id} → {args.status}")


def cmd_history(args):
    con = connect()
    ch = find_channel(con, args.channel)
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM snapshots WHERE channel_id=? ORDER BY taken_at DESC LIMIT ?",
        (ch["id"], args.limit),
    )]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("No snapshots.")
        return
    print(f"{'TAKEN':20} {'SUBS':>6} {'VIEWS':>8} {'UP28':>5} {'TYPICAL':>8} {'MOM':>6} {'ΔSUBS':>6} {'ANALYTICS':>9}")
    for r in rows:
        print(
            f"{r['taken_at'][:19]:20} {fmt_int(r['subs']):>6} {fmt_int(r['total_views']):>8} "
            f"{fmt_int(r['uploads_in_period']):>5} {fmt_int(r['typical_views']):>8} "
            f"{fmt_momentum(r['momentum']):>6} {fmt_signed(r['subs_delta']):>6} "
            f"{'ok' if r['analytics_ok'] else 'data-only':>9}"
        )


def cmd_playbook(args):
    con = connect()
    if args.all or not args.channel:
        rows = [dict(r) for r in con.execute("SELECT * FROM channels ORDER BY title")]
        if not rows:
            raise SystemExit("No channels in the ledger. Run: python3 ceo.py sync")
        created = 0
        for ch in rows:
            path, made = ensure_playbook(con, ch, force=args.force)
            print(("created " if made else "exists  ") + str(path))
            created += 1 if made else 0
        print(f"\n{created} new playbook(s), {len(rows) - created} already present.")
        return
    ch = find_channel(con, args.channel)
    path, made = ensure_playbook(con, ch, force=args.force)
    print(path)


# --------------------------------------------------------------------------- #
# Doctor
# --------------------------------------------------------------------------- #

def cmd_doctor(args):
    ensure_dirs()
    print("Amplifier CEO — setup check\n")
    failures = 0

    def line(ok, label, detail=""):
        nonlocal failures
        mark = "✓" if ok else "✗"
        if not ok:
            failures += 1
        print(f"  {mark} {label}" + (f" — {detail}" if detail else ""))

    line(True, "State directory", str(ceo_home()))
    line(True, "Ledger", str(db_path()) + ("" if db_path().exists() else " (will be created on first sync)"))

    try:
        key = read_key(args.api_key)
        line(True, "Amplifier key", f"{key[:8]}…")
    except SystemExit as e:
        line(False, "Amplifier key", str(e))
        key = None

    amp = None
    if key:
        amp = Amplifier(args.api_url, key)
        try:
            health = requests.get(amp.base + "/api/health", timeout=30)
            line(health.ok, "Amplifier API", amp.base + f" ({health.status_code})")
        except Exception as e:
            line(False, "Amplifier API", str(e))

    remote = []
    if amp:
        try:
            remote = amp.channels()
            line(True, "Connected channels", ", ".join(c.get("title", "?") for c in remote) or "none")
        except Exception as e:
            line(False, "Connected channels", str(e))

    con = connect()
    if remote:
        for c in remote:
            title = c.get("title") or c.get("youtubeChannelId")
            try:
                token = amp.token(c["_id"])["access_token"]
                data = yt_get(token, "channels", {"part": "id", "id": c["youtubeChannelId"]})
                line(bool(data.get("items")), f"Token · {title}", "mint + Data API ok")
            except Exception as e:
                line(False, f"Token · {title}", str(e)[:160])

        first = remote[0]
        try:
            token = amp.token(first["_id"])["access_token"]
            today = date.today()
            ya_get(token, {
                "ids": f"channel=={first['youtubeChannelId']}",
                "start-date": (today - timedelta(days=1)).isoformat(),
                "end-date": today.isoformat(),
                "metrics": "views",
            })
            line(True, "YouTube Analytics API", "enabled")
        except YouTubeError as e:
            if e.is_analytics_disabled():
                url = e.enable_url or "https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com"
                line(False, "YouTube Analytics API", "disabled — enable: " + url)
            else:
                line(False, "YouTube Analytics API", str(e)[:200])
        except Exception as e:
            line(False, "YouTube Analytics API", str(e)[:200])

    rows = [dict(r) for r in con.execute("SELECT * FROM channels ORDER BY title")]
    if rows:
        missing = [r["title"] for r in rows if not (ceo_home() / "channels" / f"{slugify(r['title'])}.md").exists()]
        line(True, "Channel playbooks", f"{len(rows) - len(missing)}/{len(rows)} present")
        if missing:
            print("     Missing playbooks: " + ", ".join(missing))
            print("     Create all missing with: python3 ceo.py playbook --all")
        unskilled = [r["title"] for r in rows if not r.get("owner_skill")]
        if unskilled:
            print("     No builder skill mapped: " + ", ".join(unskilled))
    else:
        print("  · No channels in the ledger yet — run: python3 ceo.py sync")

    if remote:
        ledger_ids = {r["youtube_id"] for r in rows}
        unledgered = [c.get("title") for c in remote if c.get("youtubeChannelId") not in ledger_ids]
        line(not unledgered, "Ledger coverage", "all connected channels present" if not unledgered
             else "missing from ledger: " + ", ".join(str(x) for x in unledgered) + " — run sync")

    print()
    if failures:
        print(f"{failures} check(s) need attention. Fix those before trusting a review.")
    else:
        print("All checks passed. Run `sync` then `report`.")
    return 1 if failures else 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Amplifier CEO — portfolio ledger for all connected YouTube channels")
    parser.add_argument("--api-url", default=os.environ.get("AMPLIFIER_API_URL", DEFAULT_API))
    parser.add_argument("--api-key")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("doctor", help="check key, API, tokens, analytics, playbooks")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("sync", help="pull channel + video + analytics data into the ledger")
    p.add_argument("--channel", help="one channel (partial name ok)")
    p.add_argument("--days", type=int, default=28, choices=[7, 28, 90])
    p.add_argument("--max-videos", type=int, default=30, help="recent uploads to pull per channel")
    p.add_argument("--no-analytics", action="store_true", help="Data API only; skip the Analytics API")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("report", help="portfolio scorecard + per-channel reads + due decisions")
    p.add_argument("--channel", help="one channel (partial name ok)")
    p.add_argument("--days", type=int, default=28, choices=[7, 28, 90])
    p.add_argument("--json", action="store_true")
    p.add_argument("--out", help="write markdown or JSON to this path")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("channels", help="list the ledger")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_channels)

    p = sub.add_parser("channel-set", help="set tier, cadence, pillar, skill, status or notes")
    p.add_argument("--channel", required=True)
    p.add_argument("--tier", choices=["bet", "build", "scale", "harvest", "park"])
    p.add_argument("--auto-tier", action="store_true", help="unlock and derive tier from video count")
    p.add_argument("--cadence", type=float)
    p.add_argument("--pillar")
    p.add_argument("--skill")
    p.add_argument("--status", choices=["connected", "paused", "needs_reconnect"])
    p.add_argument("--notes")
    p.set_defaults(func=cmd_channel_set)

    p = sub.add_parser("log", help="log a decision and a review date")
    p.add_argument("--channel", help="omit for portfolio-wide")
    p.add_argument("--decision", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--review-on", help="YYYY-MM-DD (default: +14 days)")
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("outcome", help="close a decision with what happened")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--outcome", required=True)
    p.set_defaults(func=cmd_outcome)

    p = sub.add_parser("task-add", help="add an open task")
    p.add_argument("--channel")
    p.add_argument("--title", required=True)
    p.add_argument("--owner")
    p.add_argument("--due")
    p.set_defaults(func=cmd_task_add)

    p = sub.add_parser("task-done", help="close a task")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_task_done)

    p = sub.add_parser("tasks", help="list tasks")
    p.add_argument("--all", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_tasks)

    p = sub.add_parser("slate-add", help="put a video on the 14-day slate")
    p.add_argument("--channel", required=True)
    p.add_argument("--publish-on", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--format")
    p.add_argument("--status", default="planned",
                   choices=["planned", "scripted", "produced", "scheduled", "published", "dropped"])
    p.add_argument("--notes")
    p.set_defaults(func=cmd_slate_add)

    p = sub.add_parser("slate", help="list the slate")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_slate)

    p = sub.add_parser("slate-status", help="move a slate item")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--status", required=True,
                   choices=["planned", "scripted", "produced", "scheduled", "published", "dropped"])
    p.set_defaults(func=cmd_slate_status)

    p = sub.add_parser("history", help="snapshot history for one channel")
    p.add_argument("--channel", required=True)
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_history)

    p = sub.add_parser("playbook", help="create or show channel playbooks (all channels by default)")
    p.add_argument("--channel", help="one channel (partial name ok)")
    p.add_argument("--all", action="store_true", help="every channel in the ledger")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_playbook)

    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
