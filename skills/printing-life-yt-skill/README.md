# printing-life-yt-skill

End-to-end builder for "Printing Life", an English history YouTube channel in a flat 2D cartoon,
OverSimplified-inspired style: topic research, episode script, British deadpan narration with
multiple character voices, Perchance scene plates, parchment maps, title/chapter cards, speech
bubbles, SFX, thumbnail, metadata, upload via Amplifier, post-upload cleanup and analytics.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r printing-life-yt-skill "$SKILL_DIR/"
```

## Requirements

- `python3` (3.10+)
- `ffmpeg` — frames → clips, assembly, loudness
- `pip install pillow numpy` — cards, frames, SFX
- `uv` (for `uvx edge-tts`) or `pip install edge-tts` — narration (`voice.py`, multi-voice)
- Playwright + Firefox — Perchance scene plates:

  ```bash
  pip install playwright && python3 -m playwright install firefox
  ```

- Optional: `pip install camoufox` — stealthier browser for `scripts/gen_images.py`
  (falls back to Playwright Firefox automatically)
- `pip install requests` — Amplifier upload/analytics scripts
- Amplifier API key — only for upload + analytics steps

Fonts are bundled in `assets/fonts/` (Anton, Bebas Neue, Luckiest Guy — OFL/Apache), so no
system font install is needed for cards and titles.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `AMPLIFIER_API_KEY` | – | Upload + analytics (fallback `AMPLIFIER_API_KEY_FILE`, `~/.config/amplifier/agent_key`) |
| `AMPLIFIER_API_URL` | `https://amplifier-api.onrender.com` | API base |
| `AMPLIFIER_CHANNEL` | `Printing Life` | Target channel name |

## Contents

```
SKILL.md                      the skill (frontmatter name: Printing Life YouTube Video Builder)
scripts/voice.py              multi-voice edge-tts + timeline + captions
scripts/gen_images.py         Perchance scene plates (playwright / camoufox)
scripts/make_cards.py         title/chapter cards, speech bubbles, impact words
scripts/prep_frames.py        Ken Burns frame prep
scripts/assemble.py           clips → final MP4 + loudness
scripts/make_sfx.py           SFX + music bed
scripts/plib.py               shared helpers
scripts/amplifier_analytics.py, upload_to_amplifier.py, cleanup_after_upload.py
references/                   publishing, episode format, topics-and-titles, style-guide, audio-and-sfx
templates/                    script-template.md, metadata.txt
assets/fonts/                 Anton-Regular, BebasNeue-Regular, LuckiestGuy-Regular (+ README)
```

## Portability notes

- `SKILL.md` and `references/publishing.md`: absolute skill paths rewritten to
  `~/.claude/skills/printing-life-yt-skill` (adjust if you install somewhere else).
- `__pycache__` and a `.orig` backup of `gen_images.py` were dropped; everything else is a
  verbatim copy.
- No other machine-specific paths remain.
