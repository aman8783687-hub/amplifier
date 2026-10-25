# redhat-engineer-youtube

End-to-end operator for the "RedHat Engineer" YouTube channel: a daily stickman-animation
explainer channel with two formats — the default 5–7 min "How X Was Built" whiteboard explainer
and the 10–16 min dark cinematic long-form.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r redhat-engineer-youtube "$SKILL_DIR/"
```

## Requirements

- `python3` (3.10+) — pipeline scripts, state, captions, render wrappers
- `node` 20+ and `npm` — Remotion 4 renderer (`assets/remotion/` is bundled as the template;
  `scripts/scaffold_remotion.py` runs `npm install` in the scaffolded episode project)
- `ffmpeg` — assembly, loudness, thumbnails
- MongoDB — topic bank and between-run state (database `redhat_pipeline`,
  `MONGODB_URI`); see `references/setup-and-state.md`
- Optional image generation: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`,
  `CLOUDFLARE_IMAGE_MODEL`
- Network access for upload/publish steps

```bash
python3 -m pip install edge-tts numpy pillow requests playwright
node --version && ffmpeg -version
```

## Configuration

Environment variables (GitHub Actions secrets, or a local `.env` for `make-video`):

| Variable | Purpose |
|---|---|
| `MONGODB_URI` | Topic bank + `channel_state` persistence |
| `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` | Scene image generation |
| `CLOUDFLARE_IMAGE_MODEL` | Optional model override |

Locked channel config lives in the workspace's `channel_state.json` (voice ID + section presets,
style-lock prompt, loudness targets, runtime ranges, counters) — see
`references/setup-and-state.md`.

## Contents

```
SKILL.md                     the skill (frontmatter name: redhat-engineer-youtube)
references/*.md              16 topic references: script formula, captions, remotion-render,
                             voice-and-audio, compliance, character bible, setup-and-state, …
assets/main-character-sheet.png
assets/remotion/             Remotion 4 template (package.json, remotion.config.ts, tsconfig.json,
                             src/Root.tsx, src/Video.tsx, src/index.ts)
```

## Portability notes — read this

This folder is **the skill only**, not the whole pipeline. `SKILL.md` invokes companion scripts
relative to the channel workspace:

```
python3 scripts/run_episode.py <slug>
python3 scripts/generate_narration_chunks.py <slug>
python3 scripts/scaffold_remotion.py <slug>
python3 scripts/render_remotion.py <slug>
python3 scripts/deliver_episode.py <slug>
...
```

Those scripts live in the **`redhat_pipline` project**, under
`RedHatEngineer/scripts/` (plus `RedHatEngineer/channel_state.json`, `RedHatEngineer/brand/`,
`make-video`, `AGENTS.md`, `tests/`). To run this skill on another machine you need that project
too:

```bash
# bring the pipeline alongside the skill
cp -r <path-to>/redhat_pipline/RedHatEngineer/scripts /path/to/workspace/scripts
cp <path-to>/redhat_pipline/make-video /path/to/workspace/
```

Everything inside this folder is machine-independent (verified: no absolute paths). The
unquoted `description:` in the frontmatter contained `: ` and failed strict YAML parsing (as it
does in the original); it is now a single-quoted scalar with byte-identical text.
