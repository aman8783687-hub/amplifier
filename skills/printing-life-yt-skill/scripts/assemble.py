#!/usr/bin/env python3
"""Assemble an episode: camera moves, overlays, SFX, music bed, loudness.

Reads the same script.md as voice.py and the timeline from voice.py, then cuts
one clip per scene and concatenates. The edit grammar is deliberately limited:
slow push-ins, lateral pans, hard cuts, slammed keywords, speech bubbles,
lower thirds and map arrows. That is the OverSimplified-style language at a
still-image budget.

Usage:
    python3 assemble.py script.md --workdir .
    python3 assemble.py script.md --workdir . --preview 4
    python3 assemble.py script.md --workdir . --music music/bed.mp3 --music-gain 0.12
    python3 assemble.py script.md --workdir . --out final/episode.mp4

Before a full render, make sure:
    audio/timeline.json       (voice.py)
    images3/s01.jpg ...       (prep_frames.py)
    sfx/*.wav                 (make_sfx.py)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_cards  # noqa: E402
from plib import Episode, Scene, load_timeline, parse_script  # noqa: E402
from prep_frames import cover_crop  # noqa: E402

FPS = 30
W, H = 1920, 1080


def run(cmd: list[str], **kw) -> None:
    kw.setdefault("stdout", subprocess.DEVNULL)
    kw.setdefault("stderr", subprocess.DEVNULL)
    subprocess.run(cmd, check=True, **kw)


def ffprobe_duration(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]).decode().strip())


def scene_image(scene: Scene, ep: Episode, workdir: Path, build: Path) -> Path:
    """Return a 1920x1080 still for this scene."""
    if scene.card:
        parts = [p.strip() for p in scene.card.split("|")]
        main = parts[0]
        sub = parts[1] if len(parts) > 1 else ""
        out = build / "cards" / f"{scene.id}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        if scene.kind in ("title", "opening"):
            img = make_cards.title_card(ep.title, sub, ep.meta.get("PART", ""))
        else:
            img = make_cards.chapter_card(main, sub, ep.meta.get("CHAPTER_NUM", ""))
        img.save(out)
        return out

    dest = workdir / "images3" / f"{scene.id}.jpg"
    if dest.is_file():
        return dest
    src = workdir / "images2" / f"{scene.id}.jpg"
    if not src.is_file():
        raise SystemExit(
            f"missing plate for {scene.id}: expected images3/{scene.id}.jpg "
            f"or images2/{scene.id}.jpg"
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    cover_crop(im, W, H, 0.2).save(dest, quality=95)
    print(f"auto-cropped {src.name} -> images3/{dest.name}")
    return dest


def zoompan_expr(move: str, zoom: float, nframes: int) -> tuple[str, str, str]:
    """Return (z, x, y) expressions for zoompan. `on` is the output frame."""
    n = max(1, nframes)
    cx = "iw/2-(iw/zoom/2)"
    cy = "ih/2-(ih/zoom/2)"
    if move == "out":
        return f"max({zoom}-({zoom}-1)*on/{n},1.0)", cx, cy
    if move == "left":
        return f"{zoom}", f"(iw-iw/zoom)*(1-on/{n})", cy
    if move == "right":
        return f"{zoom}", f"(iw-iw/zoom)*(on/{n})", cy
    if move == "up":
        return f"{zoom}", cx, f"(ih-ih/zoom)*(1-on/{n})"
    if move == "down":
        return f"{zoom}", cx, f"(ih-ih/zoom)*(on/{n})"
    # default: in
    return f"min(1.0+({zoom}-1)*on/{n},{zoom})", cx, cy


def build_overlays(scene: Scene, entry: dict, workdir: Path, build: Path) -> list[dict]:
    """Render every PNG layer for one scene and return timing metadata."""
    ov_dir = build / "ov"
    ov_dir.mkdir(parents=True, exist_ok=True)
    layers: list[dict] = []

    for i, item in enumerate(scene.lower):
        out = ov_dir / f"{scene.id}_lower{i}.png"
        make_cards.lower_third(item["text"]).save(out)
        layers.append({
            "path": out, "kind": "text", "at": item["at"],
            "end": item["at"] + (item["dur"] or entry["duration"]),
        })

    for i, item in enumerate(scene.impacts):
        out = ov_dir / f"{scene.id}_impact{i}.png"
        make_cards.impact(item["text"]).save(out)
        layers.append({
            "path": out, "kind": "text", "at": item["at"],
            "end": item["at"] + item["dur"],
        })

    for i, line in enumerate(entry.get("lines", [])):
        if not line.get("bubble"):
            continue
        x, y = line["bubble"]
        out = ov_dir / f"{scene.id}_bubble{i}.png"
        tail = "left" if x < 0.5 else "right"
        make_cards.speech_bubble(line["text"], x, y, tail).save(out)
        layers.append({
            "path": out, "kind": "text", "at": line["start"] - 0.05,
            "end": line["start"] + line["duration"] + 0.18,
        })

    for i, item in enumerate(scene.arrows):
        x1, y1, x2, y2 = item["coords"]
        out = ov_dir / f"{scene.id}_arrow{i}.png"
        img = make_cards.arrow_png(x1, y1, x2, y2)
        img.save(out)
        layers.append({
            "path": out, "kind": "arrow",
            "at": item["at"], "end": entry["duration"],
            "cx": (x1 + x2) / 2 * W, "cy": (y1 + y2) / 2 * H,
        })

    return layers


def build_scene_clip(scene: Scene, entry: dict, ep: Episode, workdir: Path,
                     build: Path, out: Path, crf: int) -> None:
    dur = float(entry["duration"])
    if dur <= 0.2:
        raise SystemExit(f"{scene.id}: duration too short ({dur:.2f}s)")
    img = scene_image(scene, ep, workdir, build)
    audio = workdir / "audio" / f"{scene.id}.wav"
    if not audio.is_file():
        raise SystemExit(f"missing {audio}; run voice.py first")

    layers = build_overlays(scene, entry, workdir, build)
    nframes = max(1, int(round(dur * FPS)))

    move = scene.move
    zoom = scene.zoom
    if scene.card and not scene.move_set:
        move, zoom = "none", 1.0
    if move == "shake":
        z, x, y = zoompan_expr("in", 1.06, nframes)
        base_chain = (
            f"[0:v]scale=3840:2160:force_original_aspect_ratio=increase,"
            f"crop=3840:2160,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=2040x1140:fps={FPS},"
            f"crop=1920:1080:x='60+9*sin(t*55)':y='60+9*cos(t*47)',"
            f"scale=1920:1080,setsar=1,format=yuv420p[base]"
        )
    else:
        z, x, y = zoompan_expr(move, zoom, nframes)
        base_chain = (
            f"[0:v]scale=3840:2160:force_original_aspect_ratio=increase,"
            f"crop=3840:2160,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},"
            f"setsar=1,format=yuv420p[base]"
        )

    inputs = [
        "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(img),
        "-i", str(audio),
    ]
    filters = [base_chain]
    last = "[base]"

    for k, layer in enumerate(layers, start=2):
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}",
                   "-i", str(layer["path"])]
        at = max(0.0, float(layer["at"]))
        end = min(dur, max(at + 0.2, float(layer["end"])))
        fade = 0.16
        filters.append(
            f"[{k}:v]format=rgba,"
            f"fade=t=in:st={at:.3f}:d={fade}:alpha=1,"
            f"fade=t=out:st={max(at, end - fade):.3f}:d={fade}:alpha=1[ov{k}]"
        )
        if layer["kind"] == "arrow":
            px = layer["cx"]
            py = layer["cy"]
            expr = (
                f"overlay=x='{px:.1f}-w/2':y='{py:.1f}-h/2'"
                f":enable='between(t,{at:.3f},{end:.3f})'"
            )
        else:
            expr = f"overlay=x=0:y=0:enable='between(t,{at:.3f},{end:.3f})'"
        filters.append(f"{last}[ov{k}]{expr}[v{k}]")
        last = f"[v{k}]"

    # SFX: each is delayed into place, then mixed with the voice at unity.
    sfx_inputs = []
    sfx_filters = []
    mix_labels = ["[1:a]"]
    next_input = 2 + len(layers)
    for j, fx in enumerate(scene.sfx):
        path = workdir / "sfx" / f"{fx['name']}.wav"
        if not path.is_file():
            print(f"  ! {scene.id}: missing sfx/{fx['name']}.wav, skipped")
            continue
        idx = next_input
        next_input += 1
        inputs += ["-i", str(path)]
        sfx_inputs.append(path)
        delay = int(max(0.0, fx["at"]) * 1000)
        label = f"[fx{j}]"
        filters.append(
            f"[{idx}:a]volume={fx['gain']},adelay={delay}|{delay},"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo{label}"
        )
        mix_labels.append(label)

    filters.append("[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[voice]")
    mix_labels[0] = "[voice]"
    if len(mix_labels) > 1:
        filters.append(
            "".join(mix_labels) + f"amix=inputs={len(mix_labels)}:duration=first:normalize=0[aout]"
        )
        alabel = "[aout]"
    else:
        alabel = "[voice]"

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-nostdin"] + inputs + [
        "-filter_complex", ";".join(filters),
        "-map", last, "-map", alabel,
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out),
    ]
    run(cmd)
    actual = ffprobe_duration(out)
    if abs(actual - dur) > 0.12:
        print(f"  ! {scene.id}: clip {actual:.2f}s vs timeline {dur:.2f}s")


def concat_clips(clips: list[Path], out: Path, build: Path) -> None:
    listing = build / "concat.txt"
    listing.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    run(["ffmpeg", "-y", "-nostdin", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", str(out)])


def music_cues(ep: Episode, timeline: dict) -> list[dict]:
    """Turn MUSIC: directives into absolute-time cues."""
    scenes = {s["id"]: s for s in timeline["scenes"]}
    total = timeline["duration"]
    cues = []
    for scene in ep.scenes:
        if not scene.music:
            continue
        s = scenes.get(scene.id)
        if not s:
            continue
        cues.append({
            "track": scene.music["track"],
            "gain": scene.music["gain"],
            "start": s["start"],
        })
    for i, cue in enumerate(cues):
        cue["end"] = cues[i + 1]["start"] if i + 1 < len(cues) else total
        cue["duration"] = max(0.5, cue["end"] - cue["start"])
    return cues


def mix_audio(ep: Episode, timeline: dict, workdir: Path, video_in: Path,
              video_out: Path, music: Path | None, music_gain: float) -> None:
    cues = music_cues(ep, timeline) if music else []
    total = timeline["duration"]

    inputs = ["-i", str(video_in)]
    filters = []
    music_labels = []
    next_input = 1
    if music:
        # one global bed
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        filters.append(
            f"[1:a]atrim=0:{total:.3f},asetpts=N/SR/TB,"
            f"volume={music_gain},"
            f"afade=t=in:st=0:d=1.2,afade=t=out:st={max(0,total-2):.3f}:d=2[bed]"
        )
        music_labels.append("[bed]")
    else:
        # per-scene cues from MUSIC: directives
        for i, cue in enumerate(cues):
            path = workdir / "music" / cue["track"]
            if not path.is_file():
                print(f"  ! missing music/{cue['track']}, cue skipped")
                continue
            idx = next_input
            next_input += 1
            inputs += ["-stream_loop", "-1", "-i", str(path)]
            delay = int(cue["start"] * 1000)
            filters.append(
                f"[{idx}:a]atrim=0:{cue['duration']:.3f},asetpts=N/SR/TB,"
                f"volume={cue['gain']},"
                f"afade=t=in:st=0:d=0.8,"
                f"afade=t=out:st={max(0,cue['duration']-1.2):.3f}:d=1.2,"
                f"adelay={delay}|{delay},"
                f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[m{i}]"
            )
            music_labels.append(f"[m{i}]")

    if music_labels:
        if len(music_labels) > 1:
            filters.append("".join(music_labels) +
                           f"amix=inputs={len(music_labels)}:duration=longest:normalize=0[music]")
        else:
            filters.append(f"{music_labels[0]}anull[music]")
        filters.append(
            "[0:a]asplit=2[vmain][vkey];"
            "[music][vkey]sidechaincompress=threshold=0.03:ratio=10:attack=20:release=420[duck];"
            "[vmain][duck]amix=inputs=2:duration=first:normalize=0,"
            "loudnorm=I=-14:TP=-1.5:LRA=11[a]"
        )
    else:
        filters.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]")

    cmd = ["ffmpeg", "-y", "-nostdin"] + inputs + [
        "-filter_complex", ";".join(filters),
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", str(video_out),
    ]
    run(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble a Printing Life episode")
    ap.add_argument("script")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preview", type=int, default=0, help="render only the first N scenes")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--music", default=None, help="global music bed (overrides MUSIC: directives)")
    ap.add_argument("--music-gain", type=float, default=0.12)
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true",
                    help="reuse already-rendered scene clips whose duration matches")
    args = ap.parse_args()

    script_path = Path(args.script).expanduser().resolve()
    ep = parse_script(script_path)
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else script_path.parent
    build = workdir / "build"
    clips_dir = build / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    timeline = load_timeline(workdir / "audio" / "timeline.json")
    entries = {s["id"]: s for s in timeline["scenes"]}
    scenes = ep.scenes
    if args.preview:
        scenes = scenes[: args.preview]
    if args.only:
        keep = set(args.only)
        scenes = [s for s in scenes if s.id in keep]
    if not scenes:
        raise SystemExit("no scenes selected")

    missing = [s.id for s in scenes if s.id not in entries]
    if missing:
        raise SystemExit(
            f"audio/timeline.json is missing {', '.join(missing)}; "
            f"re-run voice.py for this script")

    print(f"{ep.title} — {len(scenes)} scenes, "
          f"{sum(entries[s.id]['duration'] for s in scenes):.1f}s")

    if args.dry_run:
        for s in scenes:
            e = entries[s.id]
            bubbles = sum(1 for l in e.get("lines", []) if l.get("bubble"))
            print(f"  {s.id:>4}  {e['duration']:6.2f}s  {s.move:>5}  "
                  f"{len(e.get('lines', []))} lines  {len(s.sfx)} sfx  "
                  f"{len(s.lower) + len(s.impacts) + len(s.arrows) + bubbles} overlays")
            if s.kind in {"title", "chapter"} and (s.lower or s.impacts or s.arrows or bubbles):
                print(f"       ! {s.id} is a {s.kind} card with overlays; "
                      f"effects belong over scene plates")
        return 0

    clips = []
    for i, scene in enumerate(scenes, 1):
        entry = entries.get(scene.id)
        if not entry:
            raise SystemExit(f"{scene.id} missing from audio/timeline.json; re-run voice.py")
        if scene.kind in {"title", "chapter"} and (
            scene.lower or scene.impacts or scene.arrows
            or any(l.bubble for l in scene.lines)
        ):
            print(f"  ! {scene.id}: overlay on a {scene.kind} card; "
                  f"move it to a scene plate", flush=True)
        clip = clips_dir / f"{scene.id}.mp4"
        if args.resume and clip.is_file():
            try:
                have = ffprobe_duration(clip)
            except Exception:
                have = 0.0
            if abs(have - entry["duration"]) < 0.12:
                print(f"[{i}/{len(scenes)}] {scene.id} reuse {have:.1f}s", flush=True)
                clips.append(clip)
                continue
        print(f"[{i}/{len(scenes)}] {scene.id} {entry['duration']:.1f}s", flush=True)
        build_scene_clip(scene, entry, ep, workdir, build, clip, args.crf)
        clips.append(clip)

    rough = build / "video_rough.mp4"
    concat_clips(clips, rough, build)
    print(f"rough cut: {rough} ({ffprobe_duration(rough):.1f}s)")

    out = Path(args.out).expanduser().resolve() if args.out else workdir / "final" / f"{ep.slug}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    music = None if args.no_music else (
        Path(args.music).expanduser().resolve() if args.music else None
    )
    mix_audio(ep, timeline, workdir, rough, out, music, args.music_gain)
    print(f"\nfinal: {out}")
    print(f"duration: {ffprobe_duration(out):.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
