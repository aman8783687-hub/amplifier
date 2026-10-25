#!/usr/bin/env python3
"""Cast and record an episode from script.md.

Every speaker declared in the script gets its own edge-tts voice preset. Each
line is synthesised separately, so a scene can cut between the narrator and
three characters without a single flat read.

Outputs:
    audio/lines/s01_00.mp3     one file per spoken line
    audio/s01.wav              scene audio, 48 kHz mono, gaps already inserted
    audio/timeline.json        scene + line timings for assemble.py
    captions.srt               full-episode captions for YouTube

Usage:
    python3 voice.py script.md --workdir .
    python3 voice.py script.md --workdir . --force --jobs 4
    python3 voice.py script.md --workdir . --only s03 s04

Requires edge-tts on PATH (`uvx edge-tts` also works if installed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plib import Episode, Scene, ffprobe_duration, parse_script  # noqa: E402

SR = 48000
LEAD = 0.12
GAP = 0.18
TAIL = 0.40


def find_edge_tts() -> list[str]:
    exe = shutil.which("edge-tts")
    if exe:
        return [exe]
    uvx = shutil.which("uvx")
    if uvx:
        return [uvx, "edge-tts"]
    raise SystemExit("edge-tts not found. Install with: pip install --user edge-tts")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE, **kw)


def line_key(scene_id: str, idx: int) -> str:
    return f"{scene_id}_{idx:02d}"


def synth_line(text: str, preset: dict, out_mp3: Path, force: bool,
               manifest: dict, key: str, reuse: bool = False) -> None:
    digest = hashlib.sha1(
        (text + "|" + json.dumps(preset, sort_keys=True)).encode("utf-8")
    ).hexdigest()
    if reuse and out_mp3.is_file() and out_mp3.stat().st_size > 1000:
        return
    if not force and out_mp3.is_file() and manifest.get(key) == digest:
        return
    cmd = find_edge_tts() + [
        "--text", text,
        "--write-media", str(out_mp3),
        "--voice", preset["voice"],
        f"--rate={preset['rate']}",
        f"--pitch={preset['pitch']}",
        f"--volume={preset.get('volume', '+0%')}",
    ]
    last = None
    for attempt in range(4):
        try:
            run(cmd)
            if out_mp3.is_file() and out_mp3.stat().st_size > 1000:
                manifest[key] = digest
                return
            last = "empty output"
        except subprocess.CalledProcessError as exc:
            last = (exc.stderr or b"").decode("utf-8", "replace")[-300:]
        time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"edge-tts failed for {out_mp3.name}: {last}")


def read_wav_mono(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise ValueError(f"{path} is not 16-bit mono")
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((samples * 32767.0).astype(np.int16).tobytes())


def to_wav(mp3: Path, wav: Path) -> None:
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR),
         "-c:a", "pcm_s16le", str(wav)])


def split_caption(text: str, start: float, dur: float, max_chars: int = 44) -> list[dict]:
    """Split a spoken line into readable caption cues, timed by character share."""
    words = text.split()
    if not words:
        return []
    chunks, cur = [], []
    for word in words:
        if cur and len(" ".join(cur + [word])) > max_chars:
            chunks.append(cur)
            cur = [word]
        else:
            cur.append(word)
    if cur:
        chunks.append(cur)
    total_chars = sum(len(" ".join(c)) for c in chunks) or 1
    t = start
    out = []
    for chunk in chunks:
        share = len(" ".join(chunk)) / total_chars
        d = max(0.6, dur * share)
        out.append({"start": t, "end": min(start + dur, t + d),
                    "text": " ".join(chunk)})
        t += d
    return out


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Synthesise an episode from script.md")
    ap.add_argument("script", help="path to script.md")
    ap.add_argument("--workdir", default=None, help="episode build directory (default: script folder)")
    ap.add_argument("--force", action="store_true", help="re-record even unchanged lines")
    ap.add_argument("--jobs", type=int, default=3, help="parallel edge-tts requests")
    ap.add_argument("--only", nargs="*", default=None, help="only these scene ids")
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--reuse", action="store_true",
                    help="keep existing line mp3s even if the text hash changed (offline rebuild)")
    args = ap.parse_args()

    script_path = Path(args.script).expanduser().resolve()
    ep: Episode = parse_script(script_path)
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else script_path.parent
    audio_dir = workdir / "audio"
    lines_dir = audio_dir / "lines"
    lines_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = lines_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}

    selected = set(args.only) if args.only else {s.id for s in ep.scenes}
    jobs = []
    for scene in ep.scenes:
        if scene.id not in selected:
            continue
        for idx, line in enumerate(scene.lines):
            key = line_key(scene.id, idx)
            mp3 = lines_dir / f"{key}.mp3"
            jobs.append((key, line.text, ep.voices[line.who], mp3))

    print(f"Recording {len(jobs)} lines for {len(ep.scenes)} scenes -> {audio_dir}")
    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {
            pool.submit(synth_line, text, preset, mp3, args.force, manifest, key, args.reuse): key
            for key, text, preset, mp3 in jobs
        }
        done = 0
        for fut in as_completed(futures):
            key = futures[fut]
            done += 1
            try:
                fut.result()
                print(f"  [{done}/{len(jobs)}] {key} ok", flush=True)
            except Exception as exc:  # keep going, report all failures
                failures.append((key, str(exc)))
                print(f"  [{done}/{len(jobs)}] {key} FAILED: {exc}", flush=True)
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    if failures:
        print(f"\n{len(failures)} line(s) failed. Re-run the same command to retry.",
              file=sys.stderr)
        return 1

    timeline = {"title": ep.title, "slug": ep.slug, "scenes": []}
    captions: list[dict] = []
    episode_time = 0.0
    for scene in ep.scenes:
        pieces: list[np.ndarray] = []
        line_entries = []
        cursor = LEAD
        pieces.append(np.zeros(int(SR * LEAD), dtype=np.float32))
        for idx, line in enumerate(scene.lines):
            key = line_key(scene.id, idx)
            mp3 = lines_dir / f"{key}.mp3"
            wav = lines_dir / f"{key}.wav"
            if not mp3.is_file():
                raise SystemExit(
                    f"missing {mp3}. Run: python3 voice.py {script_path} --workdir {workdir}"
                )
            if not wav.is_file() or wav.stat().st_mtime < mp3.stat().st_mtime:
                to_wav(mp3, wav)
            samples = read_wav_mono(wav)
            if len(samples) == 0:
                continue
            dur = len(samples) / SR
            line_entries.append({
                "who": line.who,
                "text": line.text,
                "start": round(cursor, 3),
                "duration": round(dur, 3),
                "bubble": list(line.bubble) if line.bubble else None,
            })
            pieces.append(samples)
            cursor += dur
            if idx < len(scene.lines) - 1:
                pieces.append(np.zeros(int(SR * GAP), dtype=np.float32))
                cursor += GAP
        pieces.append(np.zeros(int(SR * TAIL), dtype=np.float32))
        cursor += TAIL
        scene_audio = np.concatenate(pieces) if pieces else np.zeros(int(SR * 0.5), dtype=np.float32)
        duration = len(scene_audio) / SR
        if scene.duration_hint and scene.duration_hint > duration:
            extra = scene.duration_hint - duration
            scene_audio = np.concatenate([scene_audio, np.zeros(int(SR * extra), dtype=np.float32)])
            duration = len(scene_audio) / SR
        out_wav = audio_dir / f"{scene.id}.wav"
        write_wav(out_wav, scene_audio)
        timeline["scenes"].append({
            "id": scene.id,
            "kind": scene.kind,
            "title": scene.title,
            "start": round(episode_time, 3),
            "duration": round(duration, 3),
            "lines": line_entries,
        })
        if not args.no_captions:
            for entry in line_entries:
                captions.extend(split_caption(
                    entry["text"],
                    episode_time + entry["start"],
                    entry["duration"],
                ))
        episode_time += duration
        print(f"  {scene.id}: {duration:.2f}s -> {out_wav.name}")

    timeline["duration"] = round(episode_time, 3)
    (audio_dir / "timeline.json").write_text(json.dumps(timeline, indent=2))

    if not args.no_captions:
        cues = []
        for i, cue in enumerate(captions, 1):
            cues.append(f"{i}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}\n")
        (workdir / "captions.srt").write_text("\n".join(cues), encoding="utf-8")

    mins, secs = divmod(episode_time, 60)
    print(f"\nDone: {int(mins)}:{secs:04.1f}, {episode_time:.1f}s, "
          f"{len(jobs)} lines, {len(captions)} caption cues")
    print(f"Timeline: {audio_dir / 'timeline.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
