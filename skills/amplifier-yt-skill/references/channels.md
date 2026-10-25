# Channels, delegation and onboarding

## The first rule: all connected channels

**Amplifier is the source of truth, not this file.** Every channel connected in
Amplifier is in scope automatically:

- `ceo.py sync` calls `GET /api/channels` and adds any new channel to the ledger.
- A new channel gets a playbook skeleton and an onboarding task on its first sync.
- Removed channels are marked `disconnected` in the ledger, not silently deleted.
- Paused channels stay visible but get zero production attention.
- The report includes every channel in the ledger, including ones with zero
  uploads or zero snapshots.

The table below is a starting map for the current accounts, not an allowlist. If
the owner connects a fifth channel tomorrow, `sync` picks it up and the next
report includes it. If a channel is missing from Amplifier, the CEO cannot manage
it; ask the owner to connect it.

## Current portfolio (observed 2026-10-21)

Verify every row with `ceo.py channels` before quoting it. These are small
channels; the absolute numbers matter less than the stage and the pattern.

| Channel | YouTube ID | Stage | Videos | Subs | Lifetime views | Builder skill |
|---|---|---|---:|---:|---:|---|
| **Business Mafia** | `UCcm8EqvJwq9WfPdDJG06f1g` | bet | 5 | 1 | 385 | `business-mafia-yt-skill` |
| **Wild Thinking** | `UCoasLCIOR2L4StJRcPe9GzQ` | bet | 2 | 0 | 10 | `wild-thinking-yt-skill` |
| **Printing Life** | `UC80bd4q0gfzpzZlMLva4h4g` | bet | 1 | 0 | 10 | none yet |
| **RedHat Engineer** | `UCyk1x0ENtU86LJ6kOTh9xig` | build | 19 | 11 | 1,357 | none yet |

### Business Mafia

- **Promise:** the real hisaab behind everyday Indian cash businesses, in Hindi.
- **Format:** stickman explainer, 8–12 minutes, black/white/gold, 16:9, weekly.
- **Builder:** `~/.claude/skills/business-mafia-yt-skill/SKILL.md`.
- **Observed:** 5 uploads in October, 385 lifetime views, one clear outlier
  (petrol pump, 254 views) and a weak latest slate. Small sample.
- **CEO read:** packaging and topic selection, not production quality. The petrol
  pump episode proves the audience exists; the next slate should make a sequel to
  the strongest business, not a new category.

### Wild Thinking

- **Promise:** an animated day-in-the-life inside a real, rare or dangerous job.
- **Format:** English explainer, cinematic watercolour, 4–6 minutes, 16:9, weekly.
- **Builder:** `~/.claude/skills/wild-thinking-yt-skill/SKILL.md`.
- **Observed:** 2 uploads; the lighthouse episode has 11 views, the newest has 0
  after one day. Too early to judge.
- **CEO read:** protect the test. The next three videos should be the strongest
  job premises, not experiments in style. Judge at video 10.

### Printing Life

- **Promise:** not yet written. The one upload, "Your Life as Every Level of a
  Fake ID Scammer", suggests a life-as-levels / inside-an-industry format.
- **Format:** not locked.
- **Builder:** none. Do not fake one inside the CEO skill.
- **Observed:** 1 upload, 10 views. No signal.
- **CEO read:** onboarding job. Write the promise and three titles before spending
  a production run. If the format is "every level of a scammer", keep it
  documentary and defensive: explain the business and the harm, never a usable
  how-to. No fraud instruction, no templates, no evasion advice.
- **First decision:** is this a documentary channel, a business-explainer channel,
  or a "day in the life" channel? Pick one. The name "Printing Life" suggests
  print/document culture; the first upload suggests something else. Resolve the
  mismatch before video two.

### RedHat Engineer

- **Promise:** not yet written. The catalogue is science/history explainers:
  fighter jets, the chip and the Nobel, Tesla's wireless power, the mechanical
  clock, the barcode, the ATM, the river that started the Industrial Revolution.
- **Format:** likely 8–15 minute English explainers with archival/illustrative
  visuals; needs a locked style and a repeatable structure.
- **Builder:** none. Fork the Wild Thinking pipeline, but do not reuse its
  watercolour/voice identity.
- **Observed:** 19 videos, 1,357 lifetime views, 11 subs (~8 subs per 1,000 views).
  Best recent: "The Mechanical Clock That Made Time Public" at ~103 views. Latest
  upload is very new.
- **CEO read:** the most mature channel and the best conversion, but the slate is
  inconsistent. This is the strongest candidate for the `FIX` budget: a locked
  format, a repeatable title pattern, and a weekly cadence. Do not add volume until
  the packaging is consistent.

## Delegation map

| Work | Owner |
|---|---|
| Portfolio review, calls, slate, publish gate | CEO (`amplifier-yt-skill`) |
| Business Mafia production | `business-mafia-yt-skill` |
| Wild Thinking production | `wild-thinking-yt-skill` |
| Printing Life production | new channel skill (fork the closest builder) |
| RedHat Engineer production | new channel skill (fork Wild Thinking, new brand) |
| Brand, money, public commitments | Human owner |
| Packaging, SEO, audit, retention, shorts, comments | The relevant `yt-*` specialist skill (advice; the builder still owns the cut) |

A channel skill is a production contract, not a strategy document. The CEO gives
it a commission; it gives back a finished, upload-ready video. The CEO does not
rewrite its script unless the owner asks.

## Onboarding a new or unmanaged channel

1. **Connect it in Amplifier.** The CEO cannot mint a token for a channel that is
   not connected.
2. **Sync.**
   ```bash
   python3 ~/.claude/skills/amplifier-yt-skill/scripts/ceo.py sync
   ```
   The channel appears in the ledger. A playbook skeleton and an onboarding task
   are created automatically.
3. **Fill the playbook.**
   ```bash
   python3 ~/.claude/skills/amplifier-yt-skill/scripts/ceo.py playbook --channel "<name>"
   ```
   Edit `~/.amplifier/ceo/channels/<slug>.md` with the owner. Do not leave the
   promise blank.
4. **Set the stage and cadence.**
   ```bash
   python3 ~/.claude/skills/amplifier-yt-skill/scripts/ceo.py channel-set \
     --channel "<name>" --tier bet --cadence 1 \
     --pillar "<one line>" --notes "<why this channel exists>"
   ```
5. **Name the builder skill.** If none fits, create one with `skill-creator` by
   forking the closest channel skill. Change the brand, voice, visual style,
   runtime, title formulas and thumbnail rules. Do not reuse another channel's
   identity.
6. **Write three titles and thumbnails before the first production run.** If they
   are not clickable, the channel is not ready.
7. **Add a three-video test slate.** Review at video 10, not video 2.
8. **Say which channel loses attention.** A new channel is not free.

## Playbook schema

`templates/channel-playbook.md` is the one-page contract. The fields that must be
filled before production:

- **Promise** — who it is for, what every video delivers, why subscribe.
- **Format lock** — runtime, aspect, visual style, voice, captions, cadence,
  title shape, thumbnail rule.
- **Three pillars** — with a share of the slate; one pillar must be the proven
  winner if there is one.
- **Kill list** — topics that failed and are not coming back.
- **Packaging rules** — title formulas that worked, thumbnail rules, first 30s.
- **Builder skill** — the exact skill name and path.
- **Metrics and targets** — 30/90-day targets and the north-star metric.
- **Guardrails** — what this channel never does.
- **Delegation** — who decides what.
- **Change log** — date, change, why.

If a playbook is vague, the channel skill will improvise, and the portfolio will
drift. The playbook is where the CEO's taste becomes repeatable.

## Creating a builder skill for an unmanaged channel

Use the `skill-creator` skill. The shortest reliable path:

1. Open the closest existing builder skill:
   - `~/.claude/skills/wild-thinking-yt-skill/SKILL.md` for English explainers.
   - `~/.claude/skills/business-mafia-yt-skill/SKILL.md` for Hindi stickman
     business stories.
2. Copy the pipeline, not the brand. Keep the ffmpeg/TTS/caption/QA mechanics;
   replace the promise, voice, palette, runtime, title formulas and thumbnail
   rules.
3. Lock the visual style in the skill. A channel that changes its look every video
   never accumulates recognition.
4. Add a QA checklist and a "never do this" list.
5. Test one full video end to end before adding the channel to the weekly slate.
6. Register the skill name in the channel playbook and in `channel-set --skill`.

Do not let a builder skill publish public on its own. The CEO gate is the point.

## Portfolio-wide checks

Run these before a review:

```bash
SKILL_DIR="$HOME/.claude/skills/amplifier-yt-skill"

python3 "$SKILL_DIR/scripts/ceo.py" doctor
python3 "$SKILL_DIR/scripts/ceo.py" sync
python3 "$SKILL_DIR/scripts/ceo.py" channels
python3 "$SKILL_DIR/scripts/ceo.py" report
```

Questions the CEO should be able to answer after those four commands:

- Are all Amplifier-connected channels in the ledger?
- Which channels have no playbook or no builder skill?
- Which channels are paused, disconnected or past cadence?
- Which channel earned the next production slot?
- Which channel is being deliberately ignored this week, and why?

If a channel is connected but invisible in the review, the ledger is lying. Fix
that before making any content call.
