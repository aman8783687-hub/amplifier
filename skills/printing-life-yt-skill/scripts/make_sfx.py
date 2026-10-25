#!/usr/bin/env python3
"""Synthesise the channel's SFX palette from scratch (no sample licensing).

The mix is narration-first. These are punctuation, not wallpaper:
  whoosh   0.62 s  section cuts, card exits
  boom     1.20 s  a slammed fact, a cannon, an army arriving
  thud     0.35 s  a body hitting the floor, a stamp
  pop      0.18 s  a speech bubble or a bright idea
  ding     0.90 s  money, a promotion, a punchline
  sting    1.10 s  a threat, a reveal, "this will not end well"
  riser    1.50 s  a build before a chapter card
  scratch  0.55 s  record-scratch reality check (use sparingly)
  stamp    0.45 s  a verdict, a map claim, a title slam

Usage:
    python3 make_sfx.py --workdir .
"""

from __future__ import annotations

import argparse
import wave
from pathlib import Path

import numpy as np

SR = 48000


def save(path: Path, x: np.ndarray) -> None:
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    print(f"{path.name}: {len(x) / SR:.2f}s")


def norm(x: np.ndarray, peak: float = 0.55) -> np.ndarray:
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def whoosh(rng) -> np.ndarray:
    n = int(SR * 0.62)
    noise = rng.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        block = noise[i:i + seg]
        if len(block) < 8:
            continue
        cutoff = 300 + 3000 * np.sin(np.pi * min(1, i / n)) ** 2
        a = np.exp(-2 * np.pi * cutoff / SR)
        y = np.empty_like(block)
        acc = 0.0
        for j in range(len(block)):
            acc = (1 - a) * block[j] + a * acc
            y[j] = acc
        out[i:i + seg] = y
    env = (t ** 2.2) * np.exp(-3.2 * t) * 3.2
    return norm(out * env, 0.5)


def ding() -> np.ndarray:
    t = np.arange(int(SR * 0.9)) / SR
    x = (np.sin(2 * np.pi * 1174 * t) * 0.6
         + np.sin(2 * np.pi * 1760 * t) * 0.3
         + np.sin(2 * np.pi * 2349 * t) * 0.15)
    x *= np.exp(-7.5 * t)
    x[:200] *= np.linspace(0, 1, 200)
    return norm(x, 0.3)


def boom(rng) -> np.ndarray:
    dur = 1.2
    t = np.arange(int(SR * dur)) / SR
    f = 62 * np.exp(-1.6 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    low = np.sin(ph) * np.exp(-2.4 * t)
    click = rng.normal(0, 1, len(t)) * np.exp(-28 * t) * 0.5
    body = rng.normal(0, 1, len(t)) * np.exp(-7 * t) * 0.25
    return norm(low + click + body, 0.7)


def thud(rng) -> np.ndarray:
    dur = 0.35
    t = np.arange(int(SR * dur)) / SR
    f = 90 * np.exp(-8 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-18 * t)
    x += rng.normal(0, 1, len(t)) * np.exp(-40 * t) * 0.6
    return norm(x, 0.55)


def pop() -> np.ndarray:
    dur = 0.18
    t = np.arange(int(SR * dur)) / SR
    f = 280 + 900 * t / dur
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-18 * t)
    return norm(x, 0.4)


def sting() -> np.ndarray:
    dur = 1.1
    t = np.arange(int(SR * dur)) / SR
    f = 90 + 60 * (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * 0.8 + np.sin(2 * ph) * 0.2
    x *= np.minimum(t / 0.12, 1) * np.exp(-2.4 * t)
    return norm(x, 0.45)


def riser(rng) -> np.ndarray:
    dur = 1.5
    t = np.arange(int(SR * dur)) / SR
    f = 110 * (1 + 3.5 * (t / dur) ** 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) * 0.5 + np.sin(2.01 * ph) * 0.2
    noise = rng.normal(0, 1, len(t)) * 0.15
    x = (tone + noise) * (t / dur) ** 2
    x[-400:] *= np.linspace(1, 0, 400)
    return norm(x, 0.5)


def scratch(rng) -> np.ndarray:
    dur = 0.55
    t = np.arange(int(SR * dur)) / SR
    noise = rng.normal(0, 1, len(t))
    # amplitude-modulated noise reads as a rough record scratch
    mod = np.sin(2 * np.pi * (18 + 30 * t / dur) * t) ** 2
    x = noise * mod * np.exp(-2.5 * t)
    return norm(x, 0.45)


def stamp(rng) -> np.ndarray:
    dur = 0.45
    t = np.arange(int(SR * dur)) / SR
    f = 120 * np.exp(-20 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-16 * t)
    x += rng.normal(0, 1, len(t)) * np.exp(-55 * t) * 0.8
    return norm(x, 0.65)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--dir", default="sfx")
    args = ap.parse_args()
    out = Path(args.workdir).expanduser().resolve() / args.dir
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    save(out / "whoosh.wav", whoosh(rng))
    save(out / "boom.wav", boom(rng))
    save(out / "thud.wav", thud(rng))
    save(out / "pop.wav", pop())
    save(out / "ding.wav", ding())
    save(out / "sting.wav", sting())
    save(out / "riser.wav", riser(rng))
    save(out / "scratch.wav", scratch(rng))
    save(out / "stamp.wav", stamp(rng))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
