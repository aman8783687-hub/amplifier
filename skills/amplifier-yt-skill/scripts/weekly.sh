#!/usr/bin/env bash
# Weekly CEO pass: sync every connected channel, write a dated brief, print tasks.
# Safe to run from cron. It does not publish anything.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE="${AMPLIFIER_CEO_HOME:-$HOME/.amplifier/ceo}"
STAMP="$(date +%F)"
BRIEF="$STATE/reports/$STAMP.md"

mkdir -p "$STATE/reports"

python3 "$SKILL_DIR/scripts/ceo.py" sync
python3 "$SKILL_DIR/scripts/ceo.py" report --out "$BRIEF"

echo
echo "Brief: $BRIEF"
echo "Tasks:"
python3 "$SKILL_DIR/scripts/ceo.py" tasks
