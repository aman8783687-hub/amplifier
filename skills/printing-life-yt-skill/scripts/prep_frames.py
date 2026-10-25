#!/usr/bin/env python3
"""Cover-crop Perchance plates to 1920x1080 without letterbox seams.

Perchance landscape output is 768x512 (3:2), not 16:9. Padding leaves a visible
cream card around every image, so we fill and crop instead. A small upward bias
keeps hats, flags and raised fists in frame.

Usage:
    python3 prep_frames.py --workdir . --src images2 --dst images3
    python3 prep_frames.py --workdir . --only s01 s02
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def cover_crop(im: Image.Image, w: int, h: int, bias: float) -> Image.Image:
    target = w / h
    src = im.width / im.height
    if src > target:
        nh = h
        nw = int(round(h * src))
    else:
        nw = w
        nh = int(round(w / src))
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = int(round((nh - h) * max(0.0, min(1.0, bias))))
    return im.crop((left, top, left + w, top + h))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--src", default="images2")
    ap.add_argument("--dst", default="images3")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--crop-y", type=float, default=0.2,
                    help="0 keeps the top edge, 0.5 centred, 1 keeps the bottom")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--quality", type=int, default=95)
    args = ap.parse_args()

    base = Path(args.workdir).expanduser().resolve()
    src, dst = base / args.src, base / args.dst
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(list(src.glob("s*.jpg")) + list(src.glob("s*.png")))
    if args.only:
        keep = set(args.only)
        files = [f for f in files if f.stem.split("_")[0] in keep]
    if not files:
        raise SystemExit(f"no s*.jpg/png in {src}")

    for f in files:
        out = dst / (f.stem + ".jpg")
        if out.is_file() and out.stat().st_mtime > f.stat().st_mtime:
            continue
        im = Image.open(f).convert("RGB")
        cover_crop(im, args.width, args.height, args.crop_y).save(out, quality=args.quality)
        print(f"{f.name} -> {out.name}")
    print(f"{len(files)} plates -> {dst} ({args.width}x{args.height}, bias {args.crop_y})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
