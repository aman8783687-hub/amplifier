#!/usr/bin/env python3
"""Turn 3:2 Perchance frames into full-bleed 1920x1080 scene plates.

Why not scale+pad in ffmpeg: Perchance renders are never pure white (usually
#FAFAFA with a soft gradient), so padding them onto a white canvas leaves a
visible rectangular seam on every cut. Measured on the biryani episode, the
seam read as a "card" around the drawing.

Cover-crop instead: resize to fill the frame, then crop the overflow with a
small upward bias so hats and raised props are not clipped.

Usage:
  python3 prep_frames.py --workdir . --src images2 --dst images3
  python3 prep_frames.py --workdir . --src images2 --dst images3 --crop-y 0
"""

import argparse
from pathlib import Path

from PIL import Image


def cover_crop(im: Image.Image, w: int, h: int, bias: float) -> Image.Image:
    """Resize to cover w x h, then crop. bias 0.5 = centred, 0.0 = keep top."""
    target = w / h
    src = im.width / im.height
    if src > target:                      # too wide -> crop sides
        nh = h
        nw = int(round(h * src))
    else:                                 # too tall -> crop top/bottom
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
    ap.add_argument("--crop-y", type=float, default=0.16,
                    help="0 = keep the top edge, 0.5 = centred, 1 = keep the bottom")
    ap.add_argument("--quality", type=int, default=95)
    args = ap.parse_args()

    base = Path(args.workdir).expanduser().resolve()
    src, dst = base / args.src, base / args.dst
    dst.mkdir(parents=True, exist_ok=True)

    files = sorted(list(src.glob("seg*.jpg")) + list(src.glob("seg*.png")))
    if not files:
        raise SystemExit(f"no seg*.jpg/png in {src}")

    for f in files:
        im = Image.open(f).convert("RGB")
        out = cover_crop(im, args.width, args.height, args.crop_y)
        out.save(dst / (f.stem + ".jpg"), quality=args.quality)
    print(f"{len(files)} frames -> {dst} ({args.width}x{args.height}, bias {args.crop_y})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
