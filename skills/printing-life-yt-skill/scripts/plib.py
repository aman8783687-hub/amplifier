#!/usr/bin/env python3
"""Shared parsing and helpers for the Printing Life pipeline.

The episode script is the single source of truth: voice.py, gen_images.py and
assemble.py all read the same Markdown file.

Script grammar (see templates/script-template.md):

    # TITLE: The French Revolution - Part 1
    # SLUG: french-revolution-1
    # VOICE NARRATOR: en-GB-RyanNeural | +0% | +0Hz
    # VOICE LOUIS: en-GB-RyanNeural | -10% | -25Hz
    # STYLE: tintin

    ## s01 | cold open | The Hall of Mirrors
    IMG: wide shot of ...
    MOVE: in
    LOWER: VERSAILLES, 1789 | 0.8 | 4.0
    SFX: boom | 0.2 | 0.55
    ARROW: 0.25,0.62,0.65,0.4 | 1.2 | 1.0
    BUBBLE: LOUIS | 0.62,0.30
    NARRATOR: France was broke.
    LOUIS: It's fine.

Directives are uppercase KEY: value lines. Any other ALL-CAPS-KEY line is a
speaker line. Speaker keys must be declared in the VOICE headers.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
FONT_TITLE = FONTS / "Anton-Regular.ttf"
FONT_UI = FONTS / "BebasNeue-Regular.ttf"
FONT_LOGO = FONTS / "LuckiestGuy-Regular.ttf"

# Locked palette. Keep every card and overlay on this list.
INK = (33, 26, 20)
PAPER = (242, 227, 198)
PAPER_DARK = (222, 203, 167)
RED = (176, 58, 46)
RED_DARK = (128, 38, 30)
GOLD = (217, 164, 65)
NAVY = (46, 64, 87)
OLIVE = (107, 122, 79)
SKY = (168, 195, 201)
CREAM = (255, 246, 226)

DIRECTIVES = {
    "IMG", "CARD", "DUR", "MOVE", "ZOOM", "LOWER", "BUBBLE", "IMPACT",
    "SFX", "ARROW", "MUSIC", "NOTE", "TRANSITION", "SHAKE",
}

SCENE_HEADER = re.compile(r"^##\s+(?P<id>[A-Za-z0-9_-]+)\s*(?:\|\s*(?P<rest>.*))?$")
META_LINE = re.compile(r"^#\s*(?P<key>[A-Za-z_]+(?:\s+[A-Za-z_]+)?)\s*:\s*(?P<value>.+?)\s*$")
SPEAKER_LINE = re.compile(r"^(?P<who>[A-Z][A-Z0-9_]*)\s*:\s*(?P<text>.+?)\s*$")


@dataclass
class Line:
    who: str
    text: str
    bubble: tuple[float, float] | None = None


@dataclass
class Scene:
    id: str
    kind: str = "scene"
    title: str = ""
    prompt: str = ""
    card: str = ""
    duration_hint: float = 0.0
    move: str = "in"
    move_set: bool = False
    zoom: float = 1.18
    transition: str = "cut"
    lines: list[Line] = field(default_factory=list)
    lower: list[dict] = field(default_factory=list)
    impacts: list[dict] = field(default_factory=list)
    sfx: list[dict] = field(default_factory=list)
    arrows: list[dict] = field(default_factory=list)
    music: dict | None = None
    notes: list[str] = field(default_factory=list)

    def text_for_voice(self) -> str:
        return " ".join(l.text for l in self.lines).strip()


@dataclass
class Episode:
    title: str
    slug: str
    voices: dict[str, dict]
    scenes: list[Scene]
    style: str = "tintin"
    cast: dict[str, str] = field(default_factory=dict)
    meta: dict[str, str] = field(default_factory=dict)


def _parse_pipe_numbers(raw: str, count: int, defaults: list[float]) -> list[float]:
    parts = [p.strip() for p in raw.split("|")]
    out = list(defaults)
    for i in range(min(count, len(parts))):
        if parts[i] == "":
            continue
        out[i] = float(parts[i])
    return out


def _parse_voice(raw: str) -> dict:
    parts = [p.strip() for p in raw.split("|")]
    return {
        "voice": parts[0] or "en-GB-RyanNeural",
        "rate": parts[1] if len(parts) > 1 and parts[1] else "+0%",
        "pitch": parts[2] if len(parts) > 2 and parts[2] else "+0Hz",
        "volume": parts[3] if len(parts) > 3 and parts[3] else "+0%",
    }


def parse_script(path: str | Path) -> Episode:
    path = Path(path).expanduser().resolve()
    raw = path.read_text(encoding="utf-8")
    title = path.stem
    slug = ""
    style = "tintin"
    voices: dict[str, dict] = {}
    cast: dict[str, str] = {}
    meta: dict[str, str] = {}
    scenes: list[Scene] = []
    cur: Scene | None = None
    last_line: Line | None = None
    last_meta_key = ""
    pending_bubble: tuple[str, tuple[float, float]] | None = None

    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            last_line = None
            continue

        if cur is None:
            m = META_LINE.match(stripped)
            if m:
                key = m.group("key").upper()
                val = m.group("value").strip()
                if key == "TITLE":
                    title = val
                elif key == "SLUG":
                    slug = val
                elif key == "STYLE":
                    style = val.lower()
                elif key.startswith("VOICE"):
                    voices[key.split(None, 1)[1].upper()] = _parse_voice(val)
                elif key.startswith("CAST"):
                    name = key.split(None, 1)[1].upper()
                    cast[name] = val
                    last_meta_key = "CAST " + name
                else:
                    meta[key] = val
                    last_meta_key = ""
                continue
            if stripped.startswith("#") and not stripped.startswith("##"):
                # A wrapped CAST description continues on following '#' lines.
                body = stripped.lstrip("#").strip()
                if last_meta_key.startswith("CAST ") and ":" not in body:
                    name = last_meta_key.split(None, 1)[1]
                    cast[name] = (cast[name] + " " + body).strip()
                else:
                    last_meta_key = ""
                continue

        hm = SCENE_HEADER.match(stripped)
        if hm:
            rest = (hm.group("rest") or "").split("|")
            kind = rest[0].strip().lower() if rest and rest[0].strip() else "scene"
            scene_title = rest[1].strip() if len(rest) > 1 else ""
            cur = Scene(id=hm.group("id"), kind=kind, title=scene_title)
            scenes.append(cur)
            last_line = None
            continue

        if cur is None:
            continue

        # Directive?
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip().upper()
            value = value.strip()
            if key in DIRECTIVES:
                if key == "IMG":
                    cur.prompt = value
                elif key == "CARD":
                    cur.card = value
                elif key == "DUR":
                    cur.duration_hint = float(value)
                elif key == "MOVE":
                    cur.move = value.lower() or "in"
                    cur.move_set = True
                elif key == "ZOOM":
                    cur.zoom = float(value)
                elif key == "TRANSITION":
                    cur.transition = value.lower() or "cut"
                elif key == "SHAKE":
                    cur.move = "shake"
                elif key == "LOWER":
                    parts = [p.strip() for p in value.split("|")]
                    at = float(parts[1]) if len(parts) > 1 and parts[1] else 0.6
                    dur = float(parts[2]) if len(parts) > 2 and parts[2] else 4.0
                    cur.lower.append({"text": parts[0], "at": at, "dur": dur})
                elif key == "IMPACT":
                    parts = [p.strip() for p in value.split("|")]
                    at = float(parts[1]) if len(parts) > 1 and parts[1] else 0.0
                    dur = float(parts[2]) if len(parts) > 2 and parts[2] else 1.4
                    cur.impacts.append({"text": parts[0], "at": at, "dur": dur})
                elif key == "SFX":
                    parts = [p.strip() for p in value.split("|")]
                    cur.sfx.append({
                        "name": parts[0],
                        "at": float(parts[1]) if len(parts) > 1 and parts[1] else 0.0,
                        "gain": float(parts[2]) if len(parts) > 2 and parts[2] else 0.5,
                    })
                elif key == "ARROW":
                    parts = [p.strip() for p in value.split("|")]
                    nums = [float(x) for x in parts[0].split(",")]
                    if len(nums) != 4:
                        raise ValueError(f"{cur.id}: ARROW needs x1,y1,x2,y2")
                    cur.arrows.append({
                        "coords": nums,
                        "at": float(parts[1]) if len(parts) > 1 and parts[1] else 1.0,
                        "dur": float(parts[2]) if len(parts) > 2 and parts[2] else 1.0,
                    })
                elif key == "BUBBLE":
                    parts = [p.strip() for p in value.split("|")]
                    who = parts[0].upper()
                    xy = [float(x) for x in (parts[1] if len(parts) > 1 else "0.62,0.3").split(",")]
                    target = next((l for l in reversed(cur.lines) if l.who == who), None)
                    if target is not None:
                        target.bubble = (xy[0], xy[1])
                    else:
                        pending_bubble = (who, (xy[0], xy[1]))
                elif key == "MUSIC":
                    parts = [p.strip() for p in value.split("|")]
                    cur.music = {
                        "track": parts[0],
                        "gain": float(parts[1]) if len(parts) > 1 and parts[1] else 0.12,
                    }
                elif key == "NOTE":
                    cur.notes.append(value)
                continue

            # Speaker line
            sm = SPEAKER_LINE.match(stripped)
            if sm:
                who = sm.group("who").upper()
                text = sm.group("text")
                bubble = None
                if pending_bubble and pending_bubble[0] == who:
                    bubble = pending_bubble[1]
                    pending_bubble = None
                last_line = Line(who=who, text=text, bubble=bubble)
                cur.lines.append(last_line)
                continue

        # Continuation of the previous spoken line (wrapped Markdown).
        if last_line is not None:
            last_line.text = (last_line.text + " " + stripped).strip()

    if not scenes:
        raise ValueError(f"{path}: no '## sNN | kind | title' scene headers found")
    if not voices:
        voices["NARRATOR"] = _parse_voice("en-GB-RyanNeural | +0% | +0Hz")
    unknown = {l.who for s in scenes for l in s.lines} - set(voices)
    if unknown:
        raise ValueError(
            f"{path}: speakers without a VOICE header: {sorted(unknown)}. "
            f"Declared: {sorted(voices)}"
        )
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return Episode(title=title, slug=slug, voices=voices, scenes=scenes,
                   style=style, cast=cast, meta=meta)


def ffprobe_duration(path: str | Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]).decode().strip()
    return float(out)


def load_timeline(path: str | Path) -> dict:
    return json.loads(Path(path).expanduser().resolve().read_text(encoding="utf-8"))


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
