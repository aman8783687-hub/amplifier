# business-mafia-yt-skill

End-to-end builder for "Business Mafia" — a Hindi YouTube channel making 8–12 min 16:9 stickman
story videos about how everyday Indian businesses actually make money (chai wala, gym, dhaba,
dumper, politician…). Covers topic → research → Hindi script → narration → scenes → captions →
assembly → thumbnail → SEO metadata → upload → cleanup → analytics.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r business-mafia-yt-skill "$SKILL_DIR/"
```

## Requirements

- `python3` (3.10+)
- `ffmpeg` — Ken Burns zoom, concat, silence trim, loudness. ffmpeg 6.x recommended
  (libass shapes Devanagari correctly by default; do **not** pass `shaping=complex` —
  ffmpeg 6.1's `subtitles`/`ass` filter has no such option)
- **Noto Sans Devanagari Bold** font installed on the system — captions are locked to it
  (74 pt, outline 6, shadow 2.2, marginV 105)
- `uv` (for `uvx edge-tts`) or `pip install edge-tts` — narration (`hi-IN-MadhurNeural`
  primary, `hi-IN-SwaraNeural` fallback only after logging)
- `pip install pillow numpy` — frame prep and procedural SFX
- Playwright + Firefox — image generation and overlay sourcing:

  ```bash
  pip install playwright && python3 -m playwright install firefox
  ```

- `pip install requests` — Amplifier upload/analytics
- Amplifier API key — only for upload + analytics steps

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `AMPLIFIER_API_KEY` | – | Upload + analytics (fallback `AMPLIFIER_API_KEY_FILE`, `~/.config/amplifier/agent_key`) |
| `AMPLIFIER_API_URL` | `https://amplifier-api.onrender.com` | API base |
| `AMPLIFIER_CHANNEL` | `Business Mafia` | Target channel name |

## Contents

```
SKILL.md                       the skill (frontmatter name: business-mafia-yt-skill)
scripts/gen_images.py          Perchance scene plates (Playwright)
scripts/build_ass.py           captions → ASS with section presets
scripts/prep_frames.py         Ken Burns frame prep (Pillow)
scripts/make_sfx.py            procedural SFX (numpy)
scripts/mix_sfx.py             SFX track mixing (ffmpeg)
scripts/trim_silence.py        edge-tts lead-in/trailing silence removal
scripts/amplifier_analytics.py, upload_to_amplifier.py, cleanup_after_upload.py
templates/                     scaffolding templates
```

## Portability notes

- Verbatim copy except `__pycache__` removal.
- The unquoted `description:` in the frontmatter contained `: ` and failed strict YAML parsing
  (as it does in the original); it is now a single-quoted scalar. The text is byte-identical.
- No machine-specific absolute paths (verified).
- Creates its own per-episode workspace when run; nothing is written back into this folder.
