#!/usr/bin/env python3
"""Reclaim local disk after a verified YouTube upload.

Deletes the heavy build assets (scene frames, clips, narration audio, video
intermediates and the master MP4) and leaves a small, re-openable record plus
the text artefacts.

What stays:
  uploaded.json            video id, url, title, upload time, bytes freed
  final/thumbnail.jpg      thumbnail
  final/script.md          timestamped narration
  final/metadata.md        title / description / chapters / tags
  final/description.txt    the text that was actually uploaded
  final/title.txt, tags.txt
  build/*.py, build/*.md   the generator sources

What goes:
  clips/ clips_ov/ images/ images2/ images3/ audio/ audio2/ sfx/ tmp/
  *.mp4 *.wav *.mkv anywhere at the root, final/ and build/
  build/concat.txt, build/*.ass, build/*.srt

Safety:
  * requires --video-id (or a youtubeVideoId inside --record)
  * verifies the video is reachable via oEmbed unless --force
  * writes uploaded.json BEFORE deleting anything
  * refuses to run outside a directory that looks like an episode workdir
  * --dry-run prints the plan and frees nothing

Usage:
  python3 cleanup_after_upload.py --workdir ~/Downloads/business-mafia-yt \
      --video-id fkwwgxxHGQQ --title "..." --yes

  python3 cleanup_after_upload.py --workdir . --video-id X --dry-run
"""

import argparse
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

HEAVY_DIRS = ["clips", "clips_ov", "images", "images2", "images3",
              "audio", "audio2", "sfx", "tmp", "overlays", "frames"]

HEAVY_EXT = {".mp4", ".mov", ".mkv", ".webm", ".wav", ".mp3", ".m4a", ".flac"}

KEEP_NAMES = {
    "thumbnail.jpg", "thumbnail.png", "thumbnail.jpeg",
    "script.md", "metadata.md", "description.txt", "title.txt", "tags.txt",
    "uploaded.json", "README.md",
}


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} GB"


def size_of(paths) -> int:
    total = 0
    for p in paths:
        if p.is_file():
            total += p.stat().st_size
        elif p.is_dir():
            for root, _dirs, files in os.walk(p):
                for f in files:
                    try:
                        total += (Path(root) / f).stat().st_size
                    except OSError:
                        pass
    return total


def looks_like_workdir(w: Path) -> bool:
    signals = ["final", "clips", "images3", "images2", "audio", "build"]
    return any((w / s).exists() for s in signals)


def verify_on_youtube(video_id: str, timeout: int = 20) -> tuple[bool, str]:
    url = f"https://www.youtube.com/oembed?url=https://youtu.be/{video_id}&format=json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.load(r)
        return True, f"{data.get('title', '')} — {data.get('author_name', '')}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def plan(workdir: Path, keep_video: bool):
    """Return (dirs, files) that would be removed."""
    dirs, files = [], []
    for d in HEAVY_DIRS:
        p = workdir / d
        if p.is_dir():
            dirs.append(p)

    for base in (workdir, workdir / "final", workdir / "build"):
        if not base.is_dir():
            continue
        for p in base.iterdir():
            if not p.is_file():
                continue
            if p.name in KEEP_NAMES:
                continue
            if p.suffix.lower() in HEAVY_EXT:
                if keep_video and p.parent.name == "final":
                    continue
                files.append(p)
            elif base.name == "build" and p.name in {"concat.txt"}:
                files.append(p)
            elif base.name == "build" and p.suffix.lower() in {".ass", ".srt"}:
                files.append(p)
    return dirs, files


def main() -> int:
    ap = argparse.ArgumentParser(description="Delete local build assets after a verified upload")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--video-id", help="YouTube video id returned by the upload")
    ap.add_argument("--record", help="path to the upload JSON, reads youtubeVideoId")
    ap.add_argument("--title", default="")
    ap.add_argument("--channel", default="Business Mafia")
    ap.add_argument("--privacy", default="")
    ap.add_argument("--keep-video", action="store_true", help="keep final/*.mp4")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="skip the YouTube reachability check")
    ap.add_argument("--yes", action="store_true", help="do not prompt")
    args = ap.parse_args()

    w = Path(args.workdir).expanduser().resolve()
    if not w.is_dir():
        sys.exit(f"workdir not found: {w}")
    if not looks_like_workdir(w):
        sys.exit(f"refusing: {w} does not look like an episode workdir "
                 f"(no final/, clips/, images3/, audio/ or build/)")

    video_id = args.video_id
    record_in = {}
    if args.record:
        rec = Path(args.record).expanduser()
        if rec.is_file():
            record_in = json.loads(rec.read_text())
            video_id = video_id or record_in.get("youtubeVideoId")
    if not video_id:
        existing = w / "uploaded.json"
        if existing.is_file():
            video_id = json.loads(existing.read_text()).get("youtubeVideoId")
    if not video_id and not args.force:
        sys.exit("refusing: no --video-id. Pass the id from the upload, or --force to skip the check.")

    if video_id and not args.force:
        ok, detail = verify_on_youtube(video_id)
        if not ok:
            sys.exit(f"refusing: could not verify https://youtu.be/{video_id} on YouTube ({detail}). "
                     f"Nothing was deleted. Use --force only if you are sure.")
        print(f"verified on YouTube: {detail}")
    else:
        print("WARNING: skipping the YouTube check (--force)")

    dirs, files = plan(w, args.keep_video)
    if not dirs and not files:
        print("nothing to clean")
        return 0

    freed = size_of(dirs + files)
    print(f"\nwill remove {len(dirs)} directories and {len(files)} files — {human(freed)}")

    if args.dry_run:
        for d in dirs:
            print(f"  dir   {d.relative_to(w)}/  ({human(size_of([d]))})")
        for f in files:
            print(f"  file  {f.relative_to(w)}  ({human(f.stat().st_size)})")
        print("\ndry run: nothing deleted")
        return 0

    if not args.yes and sys.stdin.isatty():
        answer = input("Delete these? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("cancelled")
            return 1

    record = {
        "youtubeVideoId": video_id,
        "youtubeUrl": f"https://youtu.be/{video_id}" if video_id else None,
        "title": args.title,
        "channel": args.channel,
        "privacy": args.privacy,
        "cleanedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "freedBytes": freed,
        "freedHuman": human(freed),
        "kept": ["thumbnail.jpg (root or final/)", "final/script.md", "final/metadata.md",
                 "final/description.txt", "final/title.txt", "final/tags.txt",
                 "build/*.py", "uploaded.json"],
        "keptMasterVideo": bool(args.keep_video),
    }
    (w / "uploaded.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
    print(f"record written: {w / 'uploaded.json'}")

    errors = 0
    for d in dirs:
        try:
            shutil.rmtree(d)
        except OSError as exc:
            errors += 1
            print(f"  ! {d}: {exc}", file=sys.stderr)
    for f in files:
        try:
            f.unlink()
        except OSError as exc:
            errors += 1
            print(f"  ! {f}: {exc}", file=sys.stderr)

    remaining = size_of([w])
    print(f"\nfreed {human(freed)} — workdir now {human(remaining)}"
          + (f" ({errors} items skipped)" if errors else ""))
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
