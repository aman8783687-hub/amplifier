#!/usr/bin/env python3
"""Render every text layer in the Printing Life visual language.

The image model never draws words. All lettering is deterministic PIL output on
the locked palette, so titles stay crisp and spelling stays correct.

Commands:
    title      episode title card (1920x1080)
    chapter    act/chapter card (1920x1080)
    lower      location/date lower third (transparent 1920x1080)
    impact     slammed keyword (transparent 1920x1080)
    bubble     speech bubble (transparent 1920x1080)
    thumbnail  1280x720 YouTube thumbnail
    arrow      hand-drawn map arrow PNG

Examples:
    python3 make_cards.py title "The French Revolution" --part 1 --out cards/title.png
    python3 make_cards.py chapter "THE THREE ESTATES" --sub "1789" --out cards/ch1.png
    python3 make_cards.py lower "VERSAILLES, 1789" --out ov/s01_lower.png
    python3 make_cards.py impact "BROKE" --out ov/s01_impact.png
    python3 make_cards.py bubble "It's fine." --x 0.64 --y 0.30 --out ov/s01_bubble.png
    python3 make_cards.py thumbnail --bg images3/s01.jpg \
        --title "THE FRENCH REVOLUTION" --part 1 --out final/thumbnail.jpg
    python3 make_cards.py arrow --x1 0.25 --y1 0.62 --x2 0.65 --y2 0.4 --out ov/s01_arrow.png
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plib import (  # noqa: E402
    CREAM, FONT_LOGO, FONT_TITLE, FONT_UI, GOLD, INK, NAVY, OLIVE,
    PAPER, PAPER_DARK, RED, RED_DARK, SKY,
)

W, H = 1920, 1080


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------
def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def fit_font(path: Path, text: str, max_w: int, max_size: int, min_size: int = 24):
    """Largest size at which `text` fits max_w on one line."""
    lo, hi = min_size, max_size
    best = font(path, min_size)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = font(path, mid)
        if f.getbbox(text)[2] - f.getbbox(text)[0] <= max_w:
            best, lo = f, mid + 1
        else:
            hi = mid - 1
    return best


def wrap(text: str, f: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], []
    for word in words:
        trial = " ".join(cur + [word])
        if cur and f.getbbox(trial)[2] > max_w:
            lines.append(" ".join(cur))
            cur = [word]
        else:
            cur.append(word)
    if cur:
        lines.append(" ".join(cur))
    return lines


def text_block(draw, xy, text, f, fill, stroke=0, stroke_fill=INK,
               align="center", shadow=None, spacing=0.92):
    x, y = xy
    lines = text.split("\n")
    line_h = int(f.size * spacing)
    total = line_h * len(lines)
    if align == "center":
        y -= total // 2
    for i, line in enumerate(lines):
        bbox = f.getbbox(line)
        lw = bbox[2] - bbox[0]
        lx = x - lw // 2 if align == "center" else x
        ly = y + i * line_h
        if shadow:
            off, col = shadow
            draw.text((lx + off, ly + off), line, font=f, fill=col, stroke_width=stroke,
                      stroke_fill=col)
        draw.text((lx, ly), line, font=f, fill=fill, stroke_width=stroke,
                  stroke_fill=stroke_fill)
    return total


def paper_bg(w: int = W, h: int = H, seed: int = 3) -> Image.Image:
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[:, :] = PAPER
    grain = rng.normal(0, 6.0, (h, w, 1))
    base = np.clip(base + grain, 0, 255)
    # vertical paper fibres
    fibres = rng.normal(0, 2.5, (1, w, 1))
    base = np.clip(base + fibres, 0, 255)
    # vignette
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    vig = np.clip(1.0 - 0.16 * np.clip(r - 0.55, 0, 1.6), 0, 1)[..., None]
    base = np.clip(base * vig, 0, 255)
    img = Image.fromarray(base.astype(np.uint8), "RGB")
    # soft horizontal stain bands
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(5):
        y = rng.integers(0, h)
        d.rectangle([0, y, w, y + rng.integers(1, 4)], fill=(*PAPER_DARK, 18))
    return img


def vignette(img: Image.Image, strength: float = 0.35) -> Image.Image:
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    mask = np.clip(1 - strength * np.clip(r - 0.45, 0, 2) / 1.55, 0, 1)
    arr = np.asarray(img).astype(np.float32) * mask[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def halftone(img: Image.Image, step: int = 9, alpha: int = 7) -> Image.Image:
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(0, img.height, step):
        for x in range(0, img.width, step):
            d.ellipse([x, y, x + 1, y + 1], fill=(*INK, alpha))
    return img


def logo(img: Image.Image, xy: tuple[int, int], size: int = 92, rotate: float = -2.0) -> None:
    f = font(FONT_LOGO, size)
    text = "Printing Life"
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    layer = Image.new("RGBA", (tw + 60, th + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((30, 30), text, font=f, fill=CREAM, stroke_width=max(4, size // 12),
           stroke_fill=INK)
    layer = layer.rotate(rotate, expand=True, resample=Image.BICUBIC)
    img.paste(layer, xy, layer)


# ---------------------------------------------------------------------------
# cards
# ---------------------------------------------------------------------------
def title_card(title: str, sub: str = "", part: str = "") -> Image.Image:
    img = paper_bg(seed=11)
    d = ImageDraw.Draw(img)
    # double rule frame
    d.rectangle([46, 46, W - 46, H - 46], outline=INK, width=6)
    d.rectangle([62, 62, W - 62, H - 62], outline=INK, width=2)

    # top kicker
    fk = font(FONT_UI, 54)
    kicker = "PRINTING LIFE  PRESENTS"
    d.text((W // 2 - fk.getbbox(kicker)[2] // 2, 120), kicker, font=fk,
           fill=RED_DARK)

    # red band
    band_top, band_bot = 330, 760
    d.rectangle([0, band_top, W, band_bot], fill=RED)
    d.rectangle([0, band_top, W, band_top + 8], fill=RED_DARK)
    d.rectangle([0, band_bot - 8, W, band_bot], fill=RED_DARK)

    # title, fitted
    words = title.upper()
    f = fit_font(FONT_TITLE, words, W - 260, 220)
    lines = wrap(words, f, W - 260)
    if len(lines) > 2:
        f = fit_font(FONT_TITLE, words, W - 200, 150)
        lines = wrap(words, f, W - 200)
    body = "\n".join(lines)
    text_block(d, (W // 2, (band_top + band_bot) // 2), body, f, CREAM,
               stroke=max(4, f.size // 22), stroke_fill=INK, shadow=(8, RED_DARK))

    if part:
        fp = font(FONT_UI, 92)
        label = f"PART {part}".upper()
        lw = fp.getbbox(label)[2]
        pad = 30
        d.rounded_rectangle([W // 2 - lw // 2 - pad, band_bot + 18,
                             W // 2 + lw // 2 + pad, band_bot + 132],
                            radius=10, fill=GOLD, outline=INK, width=4)
        d.text((W // 2 - lw // 2, band_bot + 26), label, font=fp, fill=INK)

    if sub:
        fs = font(FONT_UI, 62)
        d.text((W // 2 - fs.getbbox(sub)[2] // 2, 930), sub.upper(), font=fs,
               fill=INK)

    logo(img, (W - 660, H - 235), size=62)
    return halftone(img, 10, 5)


def chapter_card(main: str, sub: str = "", num: str = "") -> Image.Image:
    img = paper_bg(seed=23)
    d = ImageDraw.Draw(img)
    d.rectangle([70, 70, W - 70, H - 70], outline=INK, width=5)

    if num:
        fn = font(FONT_TITLE, 300)
        d.text((150, 155), num.upper(), font=fn, fill=RED)

    f = fit_font(FONT_TITLE, main.upper(), W - 360, 200)
    lines = wrap(main.upper(), f, W - 360)
    body = "\n".join(lines)
    text_block(d, (W // 2, H // 2 - 40), body, f, INK,
               stroke=0, shadow=(5, PAPER_DARK))

    if sub:
        fs = font(FONT_UI, 64)
        text = sub.upper()
        tw = fs.getbbox(text)[2]
        y = H // 2 + 150
        d.rectangle([W // 2 - tw // 2 - 24, y - 12, W // 2 + tw // 2 + 24, y + 62],
                    fill=GOLD, outline=INK, width=3)
        d.text((W // 2 - tw // 2, y), text, font=fs, fill=INK)

    logo(img, (W - 640, H - 225), size=56)
    return halftone(img, 11, 5)


def lower_third(text: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = fit_font(FONT_UI, text.upper(), W - 420, 64)
    tw = f.getbbox(text.upper())[2]
    bw, bh = tw + 72, f.size + 42
    x, y = 88, H - 210
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=6, fill=(*INK, 232),
                        outline=(*CREAM, 230), width=3)
    d.rectangle([x, y, x + 14, y + bh], fill=GOLD)
    d.text((x + 38, y + 17), text.upper(), font=f, fill=CREAM)
    return img


def impact(text: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = fit_font(FONT_TITLE, text.upper(), W - 320, 210)
    tw = f.getbbox(text.upper())[2] - f.getbbox(text.upper())[0]
    rx = max(360, tw / 2 + 90)
    ry = max(240, f.size * 0.82)

    # starburst
    burst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(burst)
    cx, cy = W // 2, H // 2
    pts = []
    random.seed(4)
    for i in range(28):
        a = i * math.tau / 28
        jitter = random.randint(-28, 28) if i % 2 == 0 else random.randint(-18, 18)
        px = rx + jitter if i % 2 == 0 else rx * 0.78 + jitter
        py = ry + jitter if i % 2 == 0 else ry * 0.78 + jitter
        pts.append((cx + px * math.cos(a), cy + py * math.sin(a)))
    bd.polygon(pts, fill=(*RED, 235), outline=(*INK, 255), width=8)
    burst = burst.rotate(-3, resample=Image.BICUBIC, center=(cx, cy))
    img.alpha_composite(burst)

    draw = ImageDraw.Draw(img)
    text_block(draw, (cx, cy), text.upper(), f, CREAM,
               stroke=max(6, f.size // 14), stroke_fill=INK, shadow=(10, RED_DARK))
    return img


def speech_bubble(text: str, x: float, y: float, tail: str | None = None) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(FONT_UI, 54)
    max_text_w = 520
    lines = wrap(text, f, max_text_w)
    line_h = int(f.size * 1.02)
    tw = max(f.getbbox(line)[2] for line in lines)
    bw, bh = max(210, tw + 62), line_h * len(lines) + 52
    cx, cy = int(x * W), int(y * H)
    left, top = cx - bw // 2, cy - bh // 2
    right, bot = left + bw, top + bh
    d.rounded_rectangle([left, top, right, bot], radius=26, fill=CREAM,
                        outline=INK, width=7)
    # tail
    if tail is None:
        tail = "left" if x < 0.5 else "right"
    if tail == "left":
        pts = [(left + 56, bot - 4), (left + 96, bot - 4), (left + 38, bot + 58)]
    elif tail == "right":
        pts = [(right - 96, bot - 4), (right - 56, bot - 4), (right - 38, bot + 58)]
    elif tail == "bottom":
        pts = [(cx - 28, bot - 4), (cx + 28, bot - 4), (cx, bot + 60)]
    else:
        pts = [(cx - 34, top + 4), (cx + 34, top + 4), (cx, top - 58)]
    d.polygon(pts, fill=CREAM, outline=INK, width=7)
    d.line([(pts[0][0] + 4, pts[0][1]), (pts[1][0] - 4, pts[1][1])], fill=CREAM, width=8)
    yy = top + 24
    for line in lines:
        d.text((cx - f.getbbox(line)[2] // 2, yy), line, font=f, fill=INK)
        yy += line_h
    return img


def arrow_png(x1: float, y1: float, x2: float, y2: float,
              color: tuple[int, int, int] = GOLD) -> Image.Image:
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    length = int(math.hypot(x2 - x1, y2 - y1) * W)
    length = max(180, min(1500, length))
    thickness = max(26, int(length * 0.1))
    w, h = length + 180, thickness * 3
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = h // 2
    shaft_end = w - 150
    d.line([(60, cy), (shaft_end, cy)], fill=color, width=thickness)
    d.line([(60, cy), (shaft_end, cy)], fill=INK, width=thickness + 10)
    d.line([(60, cy), (shaft_end, cy)], fill=color, width=thickness)
    head = [(w - 20, cy), (shaft_end - 10, cy - thickness * 1.15),
            (shaft_end - 10, cy + thickness * 1.15)]
    d.polygon(head, fill=color, outline=INK, width=10)
    img = img.rotate(-angle, expand=True, resample=Image.BICUBIC)
    return img


# ---------------------------------------------------------------------------
# thumbnail
# ---------------------------------------------------------------------------
def thumbnail(bg_path: Path, title: str, part: str = "", kicker: str = "",
              fg_left: Path | None = None, fg_right: Path | None = None) -> Image.Image:
    tw, th = 1280, 720
    bg = Image.open(bg_path).convert("RGB")
    # cover crop
    scale = max(tw / bg.width, th / bg.height)
    bg = bg.resize((int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS)
    left = (bg.width - tw) // 2
    top = (bg.height - th) // 2
    bg = bg.crop((left, top, left + tw, top + th))
    bg = vignette(bg, 0.55)
    # darken top and bottom for text
    shade = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(150):
        a = int(120 * (1 - i / 150))
        sd.rectangle([0, i, tw, i + 1], fill=(0, 0, 0, a))
    bg = Image.alpha_composite(bg.convert("RGBA"), shade)

    # optional cutouts
    for path, anchor in ((fg_left, "left"), (fg_right, "right")):
        if not path:
            continue
        fg = Image.open(path).convert("RGBA")
        target_h = int(th * 0.86)
        fg = fg.resize((int(fg.width * target_h / fg.height), target_h), Image.LANCZOS)
        x = -20 if anchor == "left" else tw - fg.width + 20
        bg.alpha_composite(fg, (x, th - fg.height + 6))

    d = ImageDraw.Draw(bg)
    # title
    f = fit_font(FONT_TITLE, title.upper(), tw - 90, 148)
    lines = wrap(title.upper(), f, tw - 90)
    if len(lines) > 2:
        f = fit_font(FONT_TITLE, title.upper(), tw - 70, 110)
        lines = wrap(title.upper(), f, tw - 70)
    yy = 26
    for line in lines:
        bbox = f.getbbox(line)
        lw = bbox[2] - bbox[0]
        d.text((tw // 2 - lw // 2 + 5, yy + 5), line, font=f, fill=INK,
               stroke_width=max(6, f.size // 14), stroke_fill=INK)
        d.text((tw // 2 - lw // 2, yy), line, font=f, fill=GOLD,
               stroke_width=max(5, f.size // 16), stroke_fill=INK)
        yy += int(f.size * 0.94)

    if part:
        label = f"PART {part}"
        fp = font(FONT_UI, 58)
        lw = fp.getbbox(label)[2]
        bx, by = 30, th - 96
        d.rounded_rectangle([bx, by, bx + lw + 52, by + 74], radius=8,
                            fill=RED, outline=INK, width=4)
        d.text((bx + 26, by + 4), label, font=fp, fill=CREAM)

    if kicker:
        fk = font(FONT_UI, 42)
        d.text((28, 22), kicker.upper(), font=fk, fill=CREAM,
               stroke_width=4, stroke_fill=INK)

    # logo plate bottom-right
    f = font(FONT_LOGO, 50)
    text = "Printing Life"
    bbox = f.getbbox(text)
    lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    plate = Image.new("RGBA", (lw + 42, lh + 34), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], radius=10,
                         fill=(*INK, 210))
    pd.text((21, 12), text, font=f, fill=CREAM, stroke_width=3, stroke_fill=INK)
    bg.alpha_composite(plate, (tw - plate.width - 24, th - plate.height - 20))

    return bg.convert("RGB")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Printing Life card renderer")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("title")
    p.add_argument("text")
    p.add_argument("--sub", default="")
    p.add_argument("--part", default="")
    p.add_argument("--out", required=True)

    p = sub.add_parser("chapter")
    p.add_argument("text")
    p.add_argument("--sub", default="")
    p.add_argument("--num", default="")
    p.add_argument("--out", required=True)

    p = sub.add_parser("lower")
    p.add_argument("text")
    p.add_argument("--out", required=True)

    p = sub.add_parser("impact")
    p.add_argument("text")
    p.add_argument("--out", required=True)

    p = sub.add_parser("bubble")
    p.add_argument("text")
    p.add_argument("--x", type=float, default=0.64)
    p.add_argument("--y", type=float, default=0.3)
    p.add_argument("--tail", default=None)
    p.add_argument("--out", required=True)

    p = sub.add_parser("thumbnail")
    p.add_argument("--bg", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--part", default="")
    p.add_argument("--kicker", default="")
    p.add_argument("--fg-left", default=None)
    p.add_argument("--fg-right", default=None)
    p.add_argument("--out", required=True)

    p = sub.add_parser("arrow")
    p.add_argument("--x1", type=float, default=0.25)
    p.add_argument("--y1", type=float, default=0.6)
    p.add_argument("--x2", type=float, default=0.65)
    p.add_argument("--y2", type=float, default=0.4)
    p.add_argument("--out", required=True)

    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.cmd == "title":
        img = title_card(args.text, args.sub, args.part)
        img.save(out, quality=95)
    elif args.cmd == "chapter":
        chapter_card(args.text, args.sub, args.num).save(out, quality=95)
    elif args.cmd == "lower":
        lower_third(args.text).save(out)
    elif args.cmd == "impact":
        impact(args.text).save(out)
    elif args.cmd == "bubble":
        speech_bubble(args.text, args.x, args.y, args.tail).save(out)
    elif args.cmd == "thumbnail":
        thumbnail(Path(args.bg), args.title, args.part, args.kicker,
                  Path(args.fg_left) if args.fg_left else None,
                  Path(args.fg_right) if args.fg_right else None).save(out, quality=94)
    elif args.cmd == "arrow":
        arrow_png(args.x1, args.y1, args.x2, args.y2).save(out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
