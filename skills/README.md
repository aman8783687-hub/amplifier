# Portable skill bundles

Eight self-contained skill folders, each one a complete copy of a skill with its own `README.md`
covering install, dependencies, configuration and portability notes. Copy a folder into any
agent's skills directory and the agent can set it up from its README alone.

## The skills

| Folder | Skill | What it does |
|---|---|---|
| `skills/amplifier-yt-skill/` | amplifier-yt-skill | CEO-level operating system for the YouTube portfolio on Amplifier: reviews, planning, calendar, publish/schedule |
| `skills/audio-generation/` | audio-generation | Text-to-speech voice/audio via `uvx edge-tts` (deduplicated copy of `edge-tts` + `voice-generation`) |
| `skills/business-mafia-yt-skill/` | business-mafia-yt-skill | Hindi stickman business-story videos, end to end |
| `skills/perchance-image-generation/` | perchance-image-generation | Free unlimited image generation on perchance.org via headless Firefox |
| `skills/printing-life-yt-skill/` | Printing Life YouTube Video Builder | English history channel, flat 2D OverSimplified-style episodes |
| `skills/product-reel-story/` | product-reel-story | 9:16 product reel from a shopping URL (Remotion) — source project `shopping_way_yt_skill` |
| `skills/redhat-engineer-youtube/` | redhat-engineer-youtube | RedHat Engineer channel operator (Remotion, MongoDB state) |
| `skills/wild-thinking-yt-skill/` | Wild Thinking YouTube Video Builder | Wild Thinking explainer videos, end to end |

Total: ~4.4 MB.

## Install one skill

```bash
SKILL_DIR="$HOME/.claude/skills"          # Claude Code / Claude app
# SKILL_DIR="$HOME/.agents/skills"        # Agent Skills standard (.agents/skills)

mkdir -p "$SKILL_DIR"
cp -r skills/<skill-folder> "$SKILL_DIR/"
```

## Install all eight

```bash
SKILL_DIR="$HOME/.claude/skills"          # or "$HOME/.agents/skills"
mkdir -p "$SKILL_DIR"
cp -r skills/* "$SKILL_DIR/"
```

Then let the agent finish setup — each folder's `README.md` lists its exact dependencies,
env vars and first-run checks. The short version:

| Skill | Needs |
|---|---|
| amplifier-yt-skill | `python3`, `requests`, Amplifier API key |
| audio-generation | `uv` (`uvx edge-tts`), network |
| business-mafia-yt-skill | `python3`, `ffmpeg` 6.x, Noto Sans Devanagari Bold, Pillow, numpy, edge-tts, Playwright, Amplifier key |
| perchance-image-generation | `python3`, Playwright + Firefox, network |
| printing-life-yt-skill | `python3`, `ffmpeg`, Pillow, numpy, edge-tts, Playwright (+ optional camoufox), Amplifier key |
| product-reel-story | `node` 20+, `npm install` in `reel/`, `ffmpeg`, `numpy`, `uv`/edge-tts, Playwright |
| redhat-engineer-youtube | `python3`, `node` 20+, `ffmpeg`, MongoDB (`MONGODB_URI`), Cloudflare image env — plus the companion `redhat_pipline` scripts (see its README) |
| wild-thinking-yt-skill | `python3`, `ffmpeg`, edge-tts, Playwright, Pillow, numpy, Amplifier key (also install `perchance-image-generation`) |

Shared external service: **Amplifier** (`AMPLIFIER_API_KEY` or `~/.config/amplifier/agent_key`,
`AMPLIFIER_API_URL`, default `https://amplifier-api.onrender.com`) — used by every skill's
upload/analytics scripts and by `amplifier-yt-skill` itself.

## What was changed to make these portable

Only machine-specific bits were touched; skill content is otherwise a verbatim copy.

1. **Removed** `__pycache__/`, one `gen_images.py.orig` backup.
2. **Rewrote** absolute skill paths in docs from `/home/devdevil/.claude/skills/<skill>` to
   `~/.claude/skills/<skill>` (`printing-life`, `wild-thinking`).
3. **Replaced hardcoded output/workspace paths with env vars:**
   - `perchance-image-generation/scripts/generate.py` → `PERCHANCE_OUTDIR` (default `./perchance_output`)
   - `wild-thinking-yt-skill/scripts/gen_images.py` → `WILD_THINKING_IMAGES` (default `./images`)
   - `wild-thinking-yt-skill/scripts/build_ass.py` → `WILD_THINKING_DIR` (default cwd)
4. **Derived paths from the script location** in `product-reel-story/reel/scripts/gen_voice.py`
   and `gen_audio.py`.
5. **Renamed** the audio skill folder to `audio-generation` and its frontmatter `name:` from
   `Edge-TTS` to `audio-generation` (description unchanged).
6. **Normalized** historical machine paths in `perchance-image-generation/references/examples.md`.
7. **Excluded generated artifacts** from `product-reel-story` (see its README): 1.3 GB → 1.6 MB.
8. **Quoted the `description:`** in `business-mafia-yt-skill` and `redhat-engineer-youtube`
   frontmatter (unquoted values contained `: ` and broke strict YAML parsers). Text unchanged.

Verified after the copy: no `/home/devdevil` path remains anywhere, all eight `SKILL.md` files
parse as strict YAML with `name` + `description`, every `scripts/*.py` compiles, and every
script/template/reference path mentioned in each `SKILL.md` resolves inside its own folder
(`redhat-engineer-youtube`'s pipeline scripts are the documented exception).

Note: `amplifier-yt-skill/references/channels.md` points at the sibling builder skills at
`~/.claude/skills/business-mafia-yt-skill` and `~/.claude/skills/wild-thinking-yt-skill` — install
all eight together and those links resolve.

## Notes for the receiving agent

- Read `<skill>/README.md` before running anything; it lists deps, env vars and what is
  intentionally missing.
- `redhat-engineer-youtube` is the skill only — its pipeline scripts live in the
  `redhat_pipline` project (`RedHatEngineer/scripts/`). Its README explains what else to bring.
- `wild-thinking-yt-skill` uses `perchance-image-generation` for step 3; install both.
