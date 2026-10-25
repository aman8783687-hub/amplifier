# amplifier

Skills + setup for the Amplifier YouTube portfolio (Business Mafia, Wild Thinking,
Printing Life, RedHat Engineer, Shopping Way).

Everything needed to rebuild the working environment lives in this repo, so a stopped or
rebuilt codespace can be restored in one command.

## Restore after starting / rebuilding the codespace

```bash
git clone https://github.com/aman8783687-hub/amplifier && cd amplifier
export AMPLIFIER_API_KEY=...        # or pre-place ~/.config/amplifier/agent_key
./setup.sh
```

`setup.sh` installs the 8 skills into `~/.claude/skills` (picked up by Claude Code and
OpenCode), plus ffmpeg + Noto fonts, Python deps, `uv`, Playwright browsers and the
Remotion `node_modules`, then runs the Amplifier doctor. It is idempotent.

Flags: `SKILL_DIR=~/.agents/skills`, `SKILLS_ONLY=1`.

## What is in here

| Path | Purpose |
|---|---|
| `skills/` | 8 portable skill folders, each with its own `README.md` |
| `setup.sh` | one-shot environment bootstrap |
| `AGENTS.md` | repo agent instructions + Amplifier API/secrets reference |

`skills/README.md` documents each skill, its dependencies, env vars and portability notes.

## Secrets

Never committed. The Amplifier API key lives at `~/.config/amplifier/agent_key` (mode 600),
or in `$AMPLIFIER_API_KEY` (e.g. a GitHub Actions secret). `.gitignore` blocks keys, `.env`
files, generated media, `node_modules` and local databases.
