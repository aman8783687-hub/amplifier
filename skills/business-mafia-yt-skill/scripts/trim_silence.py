#!/usr/bin/env python3
"""Remove edge-tts dead air and keep the captions in sync.

Why this exists: edge-tts returns ~0.2 s of lead-in and ~1.0-1.5 s of trailing
silence on *every* call, plus ~1.2 s at every danda (।). Concatenated raw, a
6-minute script becomes an 8.5-minute video that feels like it is stalling
between every sentence. Measured on the biryani episode: 154 s of the 517 s
runtime was silence (30%).

This trims to a fixed budget and remaps every SRT cue through the exact cut
points, so captions stay frame-accurate:

  lead-in   0.06 s
  tail      0.20 s
  internal  0.38 s max (natural sentence pause)
  detection -42 dBFS, runs >= 0.20 s only (never clips soft consonants)

Usage:
  python3 trim_silence.py --workdir .                 # audio/ -> audio2/
  python3 trim_silence.py --workdir . --mid 0.30 --tail 0.15
"""

import argparse
import os
import re
import subprocess
import wave
from pathlib import Path

import numpy as np


def load(path: Path, sr: int) -> np.ndarray:
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le",
         "-ac", "1", "-ar", str(sr), "-"])
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def silence_runs(x: np.ndarray, sr: int, threshold: float, min_sil: float):
    frame = max(1, int(sr * 0.01))  # 10 ms
    n = len(x) // frame
    if n == 0:
        return []
    rms = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
    sil = rms < threshold
    runs, i = [], 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            runs.append([i * frame, j * frame])
            i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < int(0.05 * sr):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(s, e) for s, e in merged if (e - s) / sr >= min_sil]


def remap_factory(plan, sr):
    def remap(t: float) -> float:
        shift = 0.0
        for s, e, keep in plan:
            s_s, e_s = s / sr, e / sr
            if t <= s_s:
                return t - shift
            if t < e_s:
                return s_s - shift + min(t - s_s, keep)
            shift += (e_s - s_s) - keep
        return t - shift
    return remap


def fmt(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    t %= 3600
    m = int(t // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def process(seg_path: Path, srt_path: Path, out_dir: Path, args):
    x = load(seg_path, args.sr)
    runs = silence_runs(x, args.sr, args.threshold, args.min_sil)
    plan = []
    for s, e in runs:
        d = (e - s) / args.sr
        if s <= int(0.02 * args.sr):
            keep = args.lead
        elif e >= len(x) - int(0.02 * args.sr):
            keep = args.tail
        else:
            keep = args.mid
        if d > keep:
            plan.append((s, e, keep))

    out, cursor = [], 0
    for s, e, keep in plan:
        out.append(x[cursor:s])
        out.append(x[s:s + int(keep * args.sr)])
        cursor = e
    out.append(x[cursor:])
    y = np.clip(np.concatenate(out) if out else x, -1, 1)

    with wave.open(str(out_dir / (seg_path.stem + ".wav")), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(args.sr)
        w.writeframes((y * 32767).astype(np.int16).tobytes())

    if srt_path.is_file():
        remap = remap_factory(plan, args.sr)
        clip_len = len(y) / args.sr

        def fix(m):
            a = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000
            b = int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000
            na, nb = remap(a), remap(b)
            if nb - na < 0.30:
                nb = na + 0.30
            nb = min(nb, clip_len)
            return f"{fmt(na)} --> {fmt(nb)}"

        src = srt_path.read_text()
        out_srt = re.sub(
            r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})",
            fix, src)
        (out_dir / (seg_path.stem + ".srt")).write_text(out_srt)

    return len(x) / args.sr, clip_len


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--src", default="audio")
    ap.add_argument("--dst", default="audio2")
    ap.add_argument("--lead", type=float, default=0.06)
    ap.add_argument("--tail", type=float, default=0.20)
    ap.add_argument("--mid", type=float, default=0.38)
    ap.add_argument("--min-sil", type=float, default=0.20)
    ap.add_argument("--threshold", type=float, default=0.008)
    ap.add_argument("--sr", type=int, default=48000)
    args = ap.parse_args()

    base = Path(args.workdir).expanduser().resolve()
    src = base / args.src
    dst = base / args.dst
    dst.mkdir(parents=True, exist_ok=True)

    segs = sorted(src.glob("seg*.mp3"))
    if not segs:
        raise SystemExit(f"no seg*.mp3 in {src}")

    before = after = 0.0
    for p in segs:
        a, b = process(p, p.with_suffix(".srt"), dst, args)
        before += a
        after += b

    print(f"{len(segs)} segments")
    print(f"before {before:.1f}s ({before/60:.2f} min)  after {after:.1f}s ({after/60:.2f} min)")
    print(f"removed {before-after:.1f}s of dead air ({100*(before-after)/before:.0f}%)")
    if after / 60 < 8:
        print(f"NOTE: {after/60:.2f} min is under the 8-minute floor. "
              f"Add beats (18-22 words each) instead of keeping silence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
