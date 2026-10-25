# perchance-image-generation

Free, unlimited AI image generation on perchance.org's text-to-image generator. Perchance has no
usable API, so the skill drives the real site with masked headless Firefox via Playwright and
extracts the inline base64 pixels. No login, no API key, $0.

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r perchance-image-generation "$SKILL_DIR/"
```

## Requirements

- `python3` (3.10+)
- Playwright + Firefox:

  ```bash
  pip install playwright
  python3 -m playwright install firefox
  ```

- Network access to perchance.org

## Usage

```bash
cd ~/.claude/skills/perchance-image-generation
python3 scripts/generate.py 0 2     # args: <start index> <count>
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PERCHANCE_OUTDIR` | `./perchance_output` | Where generated JPGs are written |

Set it if you want the output in a fixed workspace instead of the current directory:

```bash
PERCHANCE_OUTDIR=~/projects/my-book/images python3 scripts/generate.py 0 10
```

To change style/shape/subjects, edit `SUBJECTS`, `STYLE_SUFFIX`, `PICK_JS` and `OUTDIR` in
`scripts/generate.py` — see `references/examples.md` for tested presets (KDP coloring pages,
cinematic watercolor).

## Contents

```
SKILL.md                    the skill (frontmatter name: perchance-image-generation)
scripts/generate.py         Playwright bulk generator
references/playbook.md      how the site is driven and how failures are handled
references/examples.md      tested style/shape presets
```

## Portability notes

- `scripts/generate.py`: the hardcoded output directory was replaced with the `PERCHANCE_OUTDIR`
  env var (default `./perchance_output`).
- `references/examples.md`: absolute paths from the original machine were replaced with pointers
  into `scripts/generate.py`.
- No other machine-specific paths remain.
