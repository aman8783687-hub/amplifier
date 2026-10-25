# amplifier-yt-skill

CEO-level operating system for a portfolio of YouTube channels connected to Amplifier: portfolio
reviews, weekly planning, content calendar, per-channel grow/fix/park calls, publishing and
scheduling through the Amplifier API.

Read `SKILL.md` first — it owns portfolio strategy and delegates production to each channel's
builder skill (business-mafia, wild-thinking, printing-life, redhat-engineer).

## Install

```bash
SKILL_DIR="$HOME/.claude/skills"        # or "$HOME/.agents/skills" for the Agent Skills standard
mkdir -p "$SKILL_DIR"
cp -r amplifier-yt-skill "$SKILL_DIR/"
```

## Requirements

- `python3` (3.10+)
- `pip install requests` — used by `scripts/ceo.py` and `scripts/publish.py`
- `bash` — `scripts/weekly.sh`
- Network access to the Amplifier API

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `AMPLIFIER_API_KEY` | – | API key; if unset, falls back to `AMPLIFIER_API_KEY_FILE` |
| `AMPLIFIER_API_KEY_FILE` | `~/.config/amplifier/agent_key` | File containing the key |
| `AMPLIFIER_API_URL` | `https://amplifier-api.onrender.com` | API base URL |
| `AMPLIFIER_CEO_HOME` | `~/.amplifier/ceo` | Ledger, reports and briefs |
| `AMPLIFIER_CHANNEL` | per-command default | Used by `scripts/ceo.py --channel` |

```bash
mkdir -p ~/.config/amplifier
printf '%s' '<your-key>' > ~/.config/amplifier/agent_key
chmod 600 ~/.config/amplifier/agent_key
```

## Contents

```
SKILL.md                 the skill itself (frontmatter name: amplifier-yt-skill)
scripts/ceo.py           portfolio review, weekly plan, channel decisions
scripts/publish.py       publish / schedule a finished video to a channel
scripts/weekly.sh        weekly brief wrapper
references/              channels.md, operating-model.md, metrics.md, publishing.md
templates/               channel-playbook.md, weekly-brief.md, slate.md
evals/evals.json         skill evals
```

## Portability notes

- Verbatim copy of the original skill; the only edit was removing `__pycache__`.
- No machine-specific absolute paths were present.
- Requires an Amplifier account + API key; without it the read-only planning prompts still work.
