#!/usr/bin/env python3
"""Synthesise the channel's three SFX from scratch (no sample files needed).

  sfx/whoosh.wav  noise through a sweeping low-pass, 0.62 s — section cuts
  sfx/ding.wav    bright three-partial bell, 0.9 s — money reveals
  sfx/sting.wav   low rising tone, 1.1 s — the [RAAZ] reveal

No background music, ever. Voice stays at full level; these sit underneath.

Usage:
  python3 make_sfx.py --workdir .
"""

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
    print(f"{path.name}: {len(x)/SR:.2f}s")


def whoosh(rng: np.random.Generator) -> np.ndarray:
    dur = 0.62
    n = int(SR * dur)
    noise = rng.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    cutoff = 300 + 3000 * np.sin(np.pi * t) ** 2
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        block = noise[i:i + seg]
        if len(block) < 8:
            continue
        a = np.exp(-2 * np.pi * cutoff[min(i, n - 1)] / SR)
        y = np.empty_like(block)
        acc = 0.0
        for j in range(len(block)):
            acc = (1 - a) * block[j] + a * acc
            y[j] = acc
        out[i:i + seg] = y
    env = (t ** 2.2) * np.exp(-3.2 * t) * 3.2
    w = out * env
    return w / (np.max(np.abs(w)) + 1e-9) * 0.55


def ding() -> np.ndarray:
    dur = 0.9
    t = np.arange(int(SR * dur)) / SR
    x = (np.sin(2 * np.pi * 1174 * t) * 0.6
         + np.sin(2 * np.pi * 1760 * t) * 0.3
         + np.sin(2 * np.pi * 2349 * t) * 0.15)
    x *= np.exp(-7.5 * t)
    x[:200] *= np.linspace(0, 1, 200)
    return x / (np.max(np.abs(x)) + 1e-9) * 0.30


def sting() -> np.ndarray:
    dur = 1.1
    t = np.arange(int(SR * dur)) / SR
    f = 90 + 60 * (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * 0.8 + np.sin(2 * ph) * 0.2
    x *= np.minimum(t / 0.12, 1) * np.exp(-2.4 * t)
    return x / (np.max(np.abs(x)) + 1e-9) * 0.45


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--dir", default="sfx")
    args = ap.parse_args()

    out = Path(args.workdir).expanduser().resolve() / args.dir
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    save(out / "whoosh.wav", whoosh(rng))
    save(out / "ding.wav", ding())
    save(out / "sting.wav", sting())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
