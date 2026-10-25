#!/usr/bin/env python3
"""SRT -> animated Devanagari ASS for the Business Mafia channel.

One cue becomes a 3-word chunk. Words appear one at a time (the current word
pops, the earlier words in the chunk stay), so the caption always shows 1-3
words and never a whole sentence.

Measured caption recipe that survived a full episode:
  font        Noto Sans Devanagari Bold 74 (1920x1080)
  outline     6 + shadow 2.2 — white text lands on both white paper and the
              Boss's black suit; 3.8 looked muddy on dark art
  marginV     105
  highlight   gold #D4A017 (#H0017A0D4), only on money words and the ~18
              topic nouns. Highlighting every business word turns the whole
              line gold and kills the accent.

Edit KEYS and MONEY per topic.

Usage:
  python3 build_ass.py --workdir . --audio audio2
"""

import argparse
import glob
import os
import re

# --- edit per topic: the words that earn the gold -------------------------
KEYS = set("""
बिरयानी प्लेट देग चिकन गैस किराया कमीशन ऐप उधार मुनाफ़ा कमाई मार्जिन
बचत हिसाब बिक्री ग्राहक सिलेंडर चावल स्टाफ कमाता
""".split())

MONEY = set("""
रुपये रुपया हज़ार लाख करोड़ सौ पचास सत्तर अस्सी साठ चालीस तीस बीस
पैंतीस उनतालीस पचासी उनतीस पच्चीस बारह ग्यारह चौदह अठारह डेढ़
""".split())

GOLD = "&H0017A0D4"
POP = "\\t(0,170,\\fscx116\\fscy116)\\t(170,340,\\fscx100\\fscy100)"


def clean(w):
    return w.strip(".,?!:;।\"'()").lower()


def is_key(w):
    c = clean(w)
    return c in KEYS or c in MONEY


def parse_srt(path):
    txt = open(path, encoding="utf-8").read()
    cues = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(
            r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})",
            lines[1])
        if not m:
            continue

        def sec(a, b, c, d):
            return int(a) * 3600 + int(b) * 60 + int(c) + int(d) / 1000.0

        cues.append((sec(m.group(1), m.group(2), m.group(3), m.group(4)),
                     sec(m.group(5), m.group(6), m.group(7), m.group(8)),
                     " ".join(lines[2:]).strip()))
    return cues


def fmt(t):
    t = max(0.0, t)
    h = int(t // 3600)
    t %= 3600
    m = int(t // 60)
    s = t % 60
    cs = int(round((s - int(s)) * 100))
    return f"{h}:{m:02d}:{int(s):02d}.{min(cs, 99):02d}"


def gold(w):
    return "{\\c" + GOLD + "&}" + w + "{\\r}"


def chunks_of(words, n=3):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= n:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def build(seg, audio_dir, out_dir, font_size, margin_v, outline):
    cues = parse_srt(os.path.join(audio_dir, seg + ".srt"))
    out = [
        "[Script Info]", "Title: Business Mafia", "ScriptType: v4.00+",
        "WrapStyle: 0", "PlayResX: 1920", "PlayResY: 1080",
        "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,Noto Sans Devanagari,{font_size},&H00FFFFFF,&H000000FF,"
        f"&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,{outline},2.2,2,70,70,{margin_v},1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for start, end, text in cues:
        words = text.split()
        if not words:
            continue
        total_chars = sum(max(1, len(w)) for w in words) or 1
        cue_dur = max(0.4, end - start)
        t = start
        for chunk in chunks_of(words):
            cchars = sum(max(1, len(w)) for w in chunk) or 1
            cdur = cue_dur * cchars / total_chars
            c_end = t + cdur
            wl = [max(1, len(w)) for w in chunk]
            wtot = sum(wl)
            ct = t
            for k, w in enumerate(chunk):
                wdur = max(0.10, cdur * wl[k] / wtot)
                ws_, we_ = ct, ct + wdur
                ct = we_
                parts = []
                for j in range(k + 1):
                    wj = chunk[j]
                    if j == k:
                        col = "{\\c" + GOLD + "&}" if is_key(wj) else "{\\c&H00FFFFFF&}"
                        parts.append(col + "{" + POP + "}" + wj + "{\\r}")
                    else:
                        parts.append(gold(wj) if is_key(wj) else wj)
                line = " ".join(parts)
                if k == 0:
                    line = "{\\fad(150,0)}" + line
                out.append(f"Dialogue: 0,{fmt(ws_)},{fmt(we_)},Default,,0,0,0,,{line}")
            t = c_end

    with open(os.path.join(out_dir, seg + ".ass"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--audio", default="audio2", help="dir holding seg*.srt")
    ap.add_argument("--font-size", type=int, default=74)
    ap.add_argument("--margin-v", type=int, default=105)
    ap.add_argument("--outline", type=float, default=6)
    args = ap.parse_args()

    base = os.path.abspath(os.path.expanduser(args.workdir))
    audio_dir = os.path.join(base, args.audio)
    srts = sorted(glob.glob(os.path.join(audio_dir, "seg*.srt")))
    if not srts:
        raise SystemExit(f"no seg*.srt in {audio_dir}")

    for srt in srts:
        seg = os.path.basename(srt)[:-4]
        build(seg, audio_dir, audio_dir, args.font_size, args.margin_v, args.outline)
    print(f"built {len(srts)} ASS files in {audio_dir}")


if __name__ == "__main__":
    main()
