# product-reel-story  (a.k.a. `shopping_way_yt_skill`)

Makes a finished 9:16 product reel (40–60 s, 1080×1920, 30 fps) from a shopping product URL:
scrape the real product assets, write a six-beat first-person voiceover, synthesize voice + score,
build it in Remotion with word-synced typography, QA stills, render, verify, and package publish
metadata. Works for any commerce site, not just Myntra.

> The folder name matches the frontmatter `name: product-reel-story`. The source project on the
> original machine was `~/development/shopping_way_yt_skill`.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r product-reel-story "$SKILL_DIR/"
```

Then install the Remotion project dependencies once:

```bash
cd "$SKILL_DIR/product-reel-story/reel" && npm install
```

## Requirements

- `node` 20+ and `npm`
- `ffmpeg` — upscaling, stills, mux, loudness (−14 LUFS target)
- `python3` (3.10+) with `numpy` — procedural underscore (`scripts/gen_audio.py`)
- `uv` (for `uvx edge-tts`) or `pip install edge-tts` — voice track with **word-level
  timestamps** (`scripts/gen_voice.py`); any TTS with word timestamps can be swapped in
- Playwright (headed persistent Firefox/Chromium profile) — product asset scraping:

  ```bash
  pip install playwright && python3 -m playwright install firefox chromium
  ```

The skill's own `## 0. Prerequisites` block in `SKILL.md` is the canonical check list.

## Contents

```
SKILL.md                 the skill (frontmatter name: product-reel-story)
make_gallery.py          builds gallery.html so the user can review scraped assets
reel/                    Remotion 4 project
  src/                   Reel.tsx, scenes S1–S6, components, timeline.json, cues/theme libs
  scripts/gen_voice.py   edge-tts voice + word timings → public/audio + src/timeline.json
  scripts/gen_audio.py   procedural underscore + accents (numpy)
  scripts/render_stills.mjs   QA stills
  public/fonts/          Anton, Inter, PlayfairDisplay (bundled)
  public/textures/       grain.png
  package.json, remotion.config.ts, tsconfig.json, README.md
```

## What was deliberately left out (regenerated per product)

| Excluded | Why | How it comes back |
|---|---|---|
| `reel/node_modules/` (816 MB) | installed, not shipped | `npm install` in `reel/` |
| `reel/out/` (334 MB) | rendered videos | `npm run render` / `render_stills.mjs` |
| `reel/public/video/`, `public/images/` (90 MB) | scraped product media | step 2 of `SKILL.md` (asset scraping) |
| `reel/public/audio/` | generated voice/score | `scripts/gen_voice.py`, `scripts/gen_audio.py` |
| `myntra_41573047/`, `reel.mp4`, `youtube_metadata.json` | one run's outputs | produced per run |

Bundle size: ~1.6 MB.

## Portability notes

- `reel/scripts/gen_voice.py` and `reel/scripts/gen_audio.py`: the hardcoded
  `/home/.../reel` base path was replaced with a path derived from the script's own location
  (`os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`), so they work wherever the
  folder is copied.
- Verified: no machine-specific absolute paths remain anywhere in this bundle.
