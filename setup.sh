#!/usr/bin/env bash
# Restore the full skills environment in a fresh codespace / container.
#
#   ./setup.sh              install into ~/.claude/skills (Claude Code + OpenCode compatible)
#   SKILL_DIR=~/.agents/skills ./setup.sh
#   SKILLS_ONLY=1 ./setup.sh  only copy the skill folders, skip dependency installs
#
# Safe to re-run: every step is idempotent.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SKILL_DIR:-$HOME/.claude/skills}"
SUDO=""
[ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null && SUDO="sudo"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- 1. copy skills
say "Installing skills into $SKILL_DIR"
mkdir -p "$SKILL_DIR"
for d in "$REPO_DIR"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "${SKILL_DIR:?}/$name"
  cp -r "$d" "$SKILL_DIR/"
  echo "  ✓ $name"
done

if [ "${SKILLS_ONLY:-0}" = "1" ]; then
  say "SKILLS_ONLY=1 — done"
  exit 0
fi

# ------------------------------------------------------------ 2. system packages
if ! command -v ffmpeg >/dev/null || ! fc-match "Noto Sans Devanagari:bold" >/dev/null 2>&1; then
  say "Installing ffmpeg + Noto fonts (Devanagari Bold)"
  $SUDO apt-get update -qq
  $SUDO apt-get install -y -qq ffmpeg fonts-noto-core fonts-noto-extra
else
  say "ffmpeg + Noto fonts already present"
fi

# --------------------------------------------------------------------- 3. python
say "Installing Python dependencies"
python3 -m pip install --quiet --upgrade requests pillow numpy edge-tts playwright

# ------------------------------------------------------------------------- 4. uv
if ! command -v uv >/dev/null; then
  say "Installing uv (for uvx edge-tts)"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
else
  say "uv already installed ($(uv --version))"
fi

# ------------------------------------------------------------ 5. playwright repos
if ! python3 -c "import playwright" >/dev/null 2>&1; then
  say "Playwright missing — skipping browser install"
else
  say "Installing Playwright Firefox + Chromium (skipped if cached)"
  python3 -m playwright install firefox chromium
fi

# -------------------------------------------------------------- 6. remotion project
REEL="$SKILL_DIR/product-reel-story/reel"
if [ -f "$REEL/package.json" ]; then
  if [ ! -d "$REEL/node_modules" ]; then
    say "Installing Remotion project deps (product-reel-story/reel)"
    (cd "$REEL" && npm install --no-audit --no-fund)
  else
    say "Remotion node_modules already present"
  fi
fi

# ------------------------------------------------------------- 7. amplifier setup
say "Amplifier configuration"
KEY_FILE="${AMPLIFIER_API_KEY_FILE:-$HOME/.config/amplifier/agent_key}"
mkdir -p "$(dirname "$KEY_FILE")"
if [ -n "${AMPLIFIER_API_KEY:-}" ]; then
  printf '%s' "$AMPLIFIER_API_KEY" > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
  echo "  ✓ key written to $KEY_FILE from \$AMPLIFIER_API_KEY"
elif [ -f "$KEY_FILE" ]; then
  echo "  ✓ key already at $KEY_FILE"
else
  echo "  ! no key: export AMPLIFIER_API_KEY=... or write $KEY_FILE (mode 600)"
fi

# ------------------------------------------------------------------ 8. smoke test
if [ -f "$SKILL_DIR/amplifier-yt-skill/scripts/ceo.py" ] && [ -f "$KEY_FILE" ]; then
  say "Running amplifier doctor"
  python3 "$SKILL_DIR/amplifier-yt-skill/scripts/ceo.py" doctor || true
fi

say "Done. Optional extras not installed here:"
echo "  • pip install camoufox                       # stealthier scrape fallback"
echo "  • export MONGODB_URI=...                     # redhat-engineer-youtube"
echo "  • export CLOUDFLARE_API_TOKEN/ACCOUNT_ID     # redhat scene images"
echo "  • enable YouTube Analytics API in Google Cloud for watch time/retention"
