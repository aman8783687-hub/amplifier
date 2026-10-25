# Metrics, diagnostics and data limits

The report is only as useful as the honesty about what it does not know. Read this
before turning a number into a decision.

## 1. Where the numbers come from

| Source | What it gives | Freshness |
|---|---|---|
| Amplifier `GET /api/channels` | connected channels, titles, status, Amplifier ids | live |
| Amplifier `GET /api/channels/:id/token` | a one-hour YouTube access token per channel | live |
| YouTube Data API `channels.list` | lifetime views, subscriber count (rounded), video count, uploads playlist | live |
| YouTube Data API `playlistItems.list` | last N uploads and publish dates | live |
| YouTube Data API `videos.list` | per-video lifetime views, likes, comments, duration | live |
| YouTube Analytics API `reports.query` | period views, watch minutes, average view duration, subs gained/lost, per-video period views | live, if enabled |
| YouTube Studio | CTR, impressions, retention curve, traffic sources, revenue | manual |

`ceo.py sync` writes all of the above into `~/.amplifier/ceo/ceo.db` except the
Studio-only metrics. The report reads the **latest snapshot per channel**.

## 2. Definitions

### Typical views

Median lifetime views of the last ten uploads.

Why median: one 5,000-view outlier should not make the next 40-view video look
like a catastrophe. Why lifetime and not 28-day: the Data API does not expose
period views per video; the Analytics API does, once enabled. The median is a
baseline, not a target.

### Momentum

Median views per day alive of the newest three **mature** uploads (at least seven
days old) divided by the same figure for the three before them.

- `≥1.15×` — the latest slate is beating the prior slate.
- `0.85–1.15×` — noise; no call.
- `≤0.85×` — the latest slate is weaker.

Why seven days: a video posted yesterday always looks like a bomb next to a video
that has had a month to accumulate views. Calling that a decline is how a CEO
talks themselves into a panic. Why views per day: it partially normalises for age.

What it is not: a traffic trend. It measures upload quality, not whether the
channel grew this week. For traffic, use the Analytics API daily series.

`—` means fewer than six mature uploads. Do not invent a trend from four videos.

### Cadence gap

`days since last upload − (7 / target videos per week)`.

A channel targeting one a week, last uploaded 12 days ago, has a gap of 5 days.
A gap over three days is a `SHIP` call. A gap over 45 days is a `PARK` decision.

### Latest-video ratio

Latest video's lifetime views ÷ typical views, **only after the video is seven
days old**. Before day seven the ratio is suppressed in the report. A 0-view video
that is one day old is not a failure; it is a video that is one day old.

### Subs per 1,000 lifetime views

`subs ÷ (lifetime views / 1000)`. A rough conversion signal.

- Under 2 — reach without conversion; fix the promise, CTA and end screen.
- 2–5 — normal for a small explainer channel.
- Over 5 — healthy; more reach is the constraint.

This is lifetime, not period, and it moves slowly. Do not use it on a channel with
under 500 lifetime views.

### Uploads in period

Uploads published in the selected window (7, 28 or 90 days). This is cadence, not
output quality.

### New-video views

Sum of lifetime views of the videos published in the window. When the Analytics
API is off, this is the closest thing to "what the new slate has done". It is not
channel traffic: old videos still get views.

### Subscriber delta

Change in the rounded subscriber count since the previous snapshot. Snapshot
cadence matters: a delta over one day is not a 28-day delta. The report labels it
as a delta since the last sync, not as a period metric.

### Period views, watch time, AVD, subs gained/lost

Only from the YouTube Analytics API. If the API is disabled, these are `—` and
must stay `—`. Never estimate them from lifetime totals and present them as period
metrics.

## 3. Benchmarks, with caveats

There is no universal "good" for a channel with 12 subscribers. Compare a channel
to itself first; use these only as coarse bands.

| Stage | Healthy signal | Warning |
|---|---|---|
| `bet` (0–9) | One video ≥2× typical; improving clickability | Ten videos, nothing above typical, no clear promise |
| `build` (10–29) | 1 in 5 uploads ≥1.5× typical; subs/1k ≥2 | Five consecutive under 0.7× typical |
| `scale` (30+) | Hit rate ≥30%; subs/1k ≥3; cadence holds | Volume up, median flat or falling |
| `harvest` | Revenue stable on lower cadence | Revenue falling faster than costs |

If the channel is under 500 views per video, the most useful benchmark is the
**first 30 seconds**, not the subscriber count.

## 4. Diagnosis by symptom

| Symptom | Most likely cause | First move | Do not |
|---|---|---|---|
| Views low, retention unknown | Packaging | Rewrite title and thumbnail; test one new angle | Re-edit the video |
| Views fine, subs low | Promise/conversion | Sharpen the channel promise, CTA and end screen; make a series | Blame the algorithm |
| Subs fine, views falling | Topic fatigue or a weak slate | Return to the best pillar; make a sequel to the last outlier | Rebrand |
| One video 3× typical | A real signal | Make two sequels immediately; study the first 30s | Rebrand the channel around it |
| Every video flat | No differentiation | Change the format or the promise, not the colour grade | Post more of the same |
| Latest 3 all weak, prior 3 strong | Slate quality | Diagnose the last three titles/hooks as a set | Assume shadowban |
| Channel dark 45+ days | Attention allocation | Park or restart with a three-video test | Let it drift |
| Auth failure | OAuth/token | Reconnect in Amplifier | Plan around it |
| Analytics API off | Google Cloud config | Enable it from the link in `doctor` | Invent watch time |

### The packaging test

Before commissioning a video, write the title and the thumbnail text. Ask:

1. Would a stranger who does not know the channel click this?
2. Does the thumbnail make the same promise as the title?
3. Does the first 30 seconds pay that promise?

If any answer is no, fix the packaging before production. This is the cheapest
lever in the entire pipeline.

### The sequel test

When a video beats 1.5× typical, do not ask "what else?" Ask "what is the next
question this audience has?" Two sequels within four weeks capture the signal
before it decays.

## 5. Analytics API: what is missing and how to fix it

The Amplifier OAuth token requests:

- `youtube.upload`
- `youtube.readonly`
- `yt-analytics.readonly`
- `youtube.force-ssl`

So the token is capable. The blocker is the **Google Cloud project**: the YouTube
Analytics API must be enabled once.

`ceo.py doctor` prints the exact link. It looks like:

```
https://console.developers.google.com/apis/api/youtubeanalytics.googleapis.com/overview?project=XXXXXXXX
```

After enabling, wait a few minutes, then:

```bash
python3 ~/.claude/skills/amplifier-yt-skill/scripts/ceo.py sync
```

What becomes available:

- true period views (7/28/90 days)
- estimated watch minutes
- average view duration
- subscribers gained and lost
- per-video period views, watch time and subs gained
- daily series for a real traffic trend

What remains Studio-only:

- impressions and click-through rate
- the audience retention curve
- traffic source breakdown in full
- revenue and RPM (YouTube Analytics API has revenue metrics, but Amplifier does
  not request the monetary scope; use Studio or add it deliberately)

If a decision truly depends on CTR or retention, ask the owner for a Studio
screenshot or CSV and say that is what you are using. Do not infer it.

## 6. Data quality rules

- **Subscriber counts are rounded** by YouTube for public data. Small deltas can
  look like zero.
- **Lifetime views never go down** (normally). A delta is always non-negative;
  a subscriber delta can be negative.
- **Snapshots are point-in-time.** Comparing a 28-day snapshot to a 90-day one is
  a category error. The report prefers the snapshot matching the selected range.
- **Small samples are noisy.** Under 500 views or under 10 uploads, read direction
  and packaging, not precise percentages.
- **One outlier is not a trend.** Three consecutive beats is.
- **The API is not the algorithm.** A flat week is not a penalty. Look at the
  slate before inventing a shadowban.
- **The report is a data pack, not a verdict.** The CEO writes the judgment.

## 7. Useful commands

```bash
SKILL_DIR="$HOME/.claude/skills/amplifier-yt-skill"

# all channels, 28 days, markdown data pack
python3 "$SKILL_DIR/scripts/ceo.py" report

# machine-readable
python3 "$SKILL_DIR/scripts/ceo.py" report --json

# one channel, last 7 days
python3 "$SKILL_DIR/scripts/ceo.py" report --channel "RedHat Engineer" --days 7

# snapshot history
python3 "$SKILL_DIR/scripts/ceo.py" history --channel "Business Mafia" --limit 12

# a single video's Amplifier analytics
python3 "$SKILL_DIR/scripts/publish.py" analytics --video <amplifierVideoId> --range 28d

# channel-level Amplifier analytics
python3 "$SKILL_DIR/scripts/publish.py" analytics --channel "Wild Thinking" --range 28d
```

## 8. Quota

The YouTube Data API default quota is 10,000 units per day. A full `sync` of four
channels costs roughly:

- `channels.list` 1 unit each = 4
- `playlistItems.list` 1 unit each = 4
- `videos.list` 1 unit per 50 ids = ~4
- token minting is not a YouTube quota cost

That is trivial. The Analytics API has its own quota, also generous for a handful
of channels. Do not optimize quota before optimizing the content.
