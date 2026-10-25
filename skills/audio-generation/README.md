# audio-generation (Edge-TTS)

Voice / audio generation: text-to-speech through Microsoft Edge's neural TTS service using
`uvx edge-tts`. Supports multiple languages and voices, rate / pitch / volume control, and
subtitle generation. No API key, no login.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r audio-generation "$SKILL_DIR/"
```

## Requirements

- [`uv`](https://docs.astral.sh/uv/) — provides `uvx`, which fetches `edge-tts` on first use:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  (pip fallback: `pip install edge-tts`, then call `edge-tts` instead of `uvx edge-tts`)
- Network access to Microsoft's Edge TTS service (the synthesis happens online)

## Usage

```bash
uvx edge-tts --text "{msg}" --write-media /tmp/out.mp3
uvx edge-tts --text "{msg}" --write-media /tmp/out.mp3 --write-subtitles -      # with subtitles
uvx edge-tts --text "{msg}" --write-media /tmp/out.mp3 --rate=+50%              # speed
uvx edge-tts --text "{msg}" --write-media /tmp/out.mp3 --voice en-US-GuyNeural  # voice
uvx edge-tts --list-voices                                                     # all voices
```

## Portability notes

- This folder is the single deduplicated copy of two byte-identical originals
  (`edge-tts/` and `voice-generation/`).
- The frontmatter `name:` was changed from `Edge-TTS` to `audio-generation` so the folder name
  and skill name match; the description (and therefore when it triggers) is unchanged.
- No machine-specific paths.
