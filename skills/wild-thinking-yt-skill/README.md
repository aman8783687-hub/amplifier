# wild-thinking-yt-skill

End-to-end builder for "Wild Thinking" explainer videos: script → Edge-TTS voice → Perchance
images → word-by-word ASS subtitles → Ken Burns dynamic edit → overlays → whoosh SFX → final
1080p MP4 → upload to Amplifier → analytics.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r wild-thinking-yt-skill "$SKILL_DIR/"
```

## Requirements

- `python3` (3.10+)
- `ffmpeg` — clips, Ken Burns zoom, concat, loudness
- `uv` (for `uvx edge-tts`) or `pip install edge-tts` — narration
- Playwright + Firefox — Perchance image generation and overlay sourcing:

  ```bash
  pip install playwright && python3 -m playwright install firefox
  ```

- `pip install pillow numpy` — image prep and SFX mixing
- Optional: `pip install camoufox` (stealthier browser; falls back to Playwright Firefox)
- Amplifier API key — only for steps 9–10 (upload + analytics)

Image generation reuses the `perchance-image-generation` skill (`SKILL.md` step 3 adapts its
`scripts/generate.py`), so install that skill alongside this one for a full pipeline.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `WILD_THINKING_DIR` | current working directory | Project workspace scanned by `scripts/build_ass.py` |
| `WILD_THINKING_IMAGES` | `./images` | Output dir for `scripts/gen_images.py` |
| `AMPLIFIER_API_KEY` | – | Upload + analytics (fallback `AMPLIFIER_API_KEY_FILE`, `~/.config/amplifier/agent_key`) |
| `AMPLIFIER_API_URL` | `https://amplifier-api.onrender.com` | API base |
| `AMPLIFIER_CHANNEL` | `Wild Thinking` | Target channel name |

```bash
export WILD_THINKING_DIR=~/projects/wild-thinking
export WILD_THINKING_IMAGES=$WILD_THINKING_DIR/images
```

## Contents

```
SKILL.md                     the skill (frontmatter name: Wild Thinking YouTube Video Builder)
scripts/gen_images.py        Perchance bulk image generator (edit SUBJECTS)
scripts/build_ass.py         SRT → animated word-by-word ASS
scripts/mix_sfx.py           iterative whoosh/ding mixer
scripts/upload_to_amplifier.py   upload finished video + register for analytics
scripts/amplifier_analytics.py   channel/video/overview stats
templates/                   scaffolding templates
```

## Portability notes

- `scripts/gen_images.py`: `OUTDIR` now reads `WILD_THINKING_IMAGES` (default `./images`).
- `scripts/build_ass.py`: `BASE` now reads `WILD_THINKING_DIR` (default `os.getcwd()`).
- `SKILL.md`: absolute skill paths rewritten to `~/.claude/skills/wild-thinking-yt-skill`.
- `__pycache__` removed. Everything else is a verbatim copy.
