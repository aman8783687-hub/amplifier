# The operating model

This is the doctrine behind the weekly loop. Read it when a decision is not
obvious, when the owner asks "why are we doing this?", or when the portfolio is
tempted to add a fifth channel instead of fixing the four that exist.

## 1. What the CEO is for

The CEO does five things, in this order:

1. **Allocates attention.** There is one operator and a finite week. The ledger
   exists to make the allocation explicit, not to make every channel feel loved.
2. **Sets the bar.** A channel is only as good as the promise its title,
   thumbnail and first thirty seconds make — and keep.
3. **Keeps cadence.** Consistency compounds; intensity does not.
4. **Makes the call.** Scale, fix, ship, hold, park. A call with a date beats a
   strong opinion with no date.
5. **Delegates the craft.** The channel builder owns the script, voice, visuals,
   edit and captions. The CEO owns the commission and the gate.

If the CEO is doing the editing, nobody is doing the allocating.

## 2. Stages

Stage is a description of evidence, not a badge.

| Stage | Entry | Exit / next review | The only question |
|---|---|---|---|
| `bet` | 0–9 videos | at video 10 | Is there a repeatable format? |
| `build` | 10–29 videos or one proven format | at video 30 or 3 consecutive hits | Which slate is winning? |
| `scale` | 30+ videos or a proven hit engine | quarterly | Can volume hold quality? |
| `harvest` | declining but monetised | quarterly | How do we protect revenue? |
| `park` | 45 days dark or a failed 10-video test | at the restart decision | Restart with a new promise, or reallocate? |

### The bet stage (0–9 videos)

Goal: find one format worth repeating. Do not judge a channel on subscribers or
revenue. Judge it on whether the last three videos are getting easier to make and
clearer to click.

At video 10, make one of three calls:

- **Double down** — at least one video beat 2× the channel's typical, and you can
  describe why in one sentence.
- **Change the promise** — the videos are competent but flat; rewrite the promise,
  not the edit.
- **Park** — ten videos, no signal, no strategic reason. Move the hours.

### The build stage (10–29 videos)

Goal: a repeatable hit rate. The channel now has a typical; the job is to beat it
on purpose. One in five videos should be an outlier. If nothing has beaten the
typical in ten uploads, the format is not differentiated enough.

### The scale stage (30+ or proven)

Goal: more of the same without a quality drop. Add cadence only when the builder
can absorb it and the QA gate still passes. Scaling a weak format just makes more
weak videos.

### Harvest and park

Harvest is for a channel that still earns but no longer grows: cut cadence,
recycle the proven winners, stop experiments.

Park is a deliberate decision, not neglect. A parked channel gets a date and a
condition: "restart with a three-video test on [promise] by [date], or remove it
from the portfolio." Until then it gets zero production hours.

## 3. The attention budget

Think of the week as 100 points, not 100 hours. A realistic solo operator has
maybe 20–25 hours of channel work a week; the points map to that.

| Allocation | Share | What it buys |
|---|---:|---|
| The best-momentum channel | 50 | The next video, packaging tests, the sequel to the outlier |
| The clearest fix | 30 | Research, rewrite, thumbnail tests, a format change |
| One experiment or new channel | 20 | The bet that could become next quarter's winner |

Rules:

- **Never split evenly.** Four channels at 25 points each is how a portfolio
  becomes four hobbies.
- **A channel with no allocation is parked on purpose.** Say it out loud.
- **New channels take from an existing one.** Name the donor.
- **The fix budget goes to the channel where one change unlocks the most.** Usually
  packaging, not another production run.
- **Protect the winner.** The channel with momentum is the one most likely to be
  neglected because it is "fine". It is not fine; it is the compounding asset.

## 4. Decision thresholds

Use these as defaults, not laws. Write down the exception when you make one.

| Call | Trigger | First action |
|---|---|---|
| `SCALE` | 3 consecutive videos ≥1.5× typical, or momentum ≥1.15× for two reviews | Double the winning pillar; add a second slot only if QA can hold |
| `FIX` | 2 consecutive videos <0.7× typical with normal cadence | Rewrite title + thumbnail; do not change the topic yet |
| `CHANGE FORMAT` | 5 consecutive videos <0.7× typical | New promise and new visual/structural format; keep the audience |
| `SHIP` | Days since upload > target interval + 3 | Produce the next commissioned video; no new strategy |
| `HOLD` | Everything inside the normal range | Keep cadence, change one variable |
| `PARK` | 45 days dark, or 10-video test with no signal | Restart test or reallocate hours |
| `ONBOARD` | 0 uploads, or a newly connected channel | Playbook + first three titles before production |
| `FIX AUTH` | Token or OAuth failure | Reconnect in Amplifier; do not plan around it |

**One outlier is not a trend.** Three consecutive beats is a trend. A single video
at 3× typical is a gift: make two sequels immediately, but do not rebrand the
channel around it.

**Two misses are not a format failure.** Five are. Changing the format after every
weak video is how a channel never accumulates an audience.

## 5. The weekly rhythm

### Monday — review and decide (60–90 minutes)

1. Sync.
2. Read the scorecard and the three channel notes that matter.
3. Write the headline before touching the slate.
4. Make at most three moves. Log them with review dates.
5. Build the 14-day slate. Every row has a channel, title, format and date.

### Tuesday to Thursday — ship (the bulk of the week)

- Commission the next video(s) to the channel builder.
- Do packaging work: titles, thumbnails, hooks.
- QA what comes back. Send it back once, with specifics.
- Publish private or unlisted; public only with the owner's yes.

### Friday — retro and next slate (45 minutes)

- What did the last upload teach? One sentence, not a report.
- Did the slate slip? Why? Fix the cause, not the date.
- Update the playbook if a rule changed.
- Close tasks. Write next week's slate.

### Daily — standup (5 minutes)

Only anomalies: auth failure, a video at 2× typical, a channel past cadence by a
week, a comment/topic worth a response. No full report. No dashboard theatre.

### Automating the data pack

The brief can run itself; the decisions cannot.

```cron
0 9 * * 1 "$HOME/.claude/skills/amplifier-yt-skill/scripts/weekly.sh" >> "$HOME/.amplifier/ceo/weekly.log" 2>&1
```

That writes a dated brief to `~/.amplifier/ceo/reports/`. Read it on Monday and
still do the review. A cron job that nobody reads is just disk usage.

## 6. The 30-minute review agenda

If the owner joins a review, protect their time:

1. **Headline** (2 min) — the one thing that matters.
2. **Numbers** (5 min) — one scorecard, no tab-by-tab walkthrough.
3. **Diagnosis** (10 min) — the top three channels, with evidence and uncertainty.
4. **Decisions** (10 min) — at most three, each with an owner and a date.
5. **Asks** (3 min) — money, access, a brand call, a public commitment. Max three.

If a topic does not change a decision, it does not belong in the meeting.

## 7. Commissioning work

Every commission has six fields:

```
CHANNEL:
TOPIC / ANGLE:
FORMAT / LENGTH:
PACKAGING (working title + thumbnail):
DEADLINE:
SUCCESS CRITERIA:
```

A commission without a working title is not ready. The title is the cheapest test
of whether the idea is interesting. If the title is weak, the video will be weak.

The channel builder owns:

- research and fact-checking
- script and structure
- voice and pronunciation
- images, motion, captions
- sound design and mix
- export and technical QA

The CEO owns:

- the topic and angle
- the packaging direction
- the deadline
- the pre-publish gate
- the publish/schedule decision
- the post-mortem and the next call

## 8. The pre-publish gate

Do not ship until all of these are true:

- [ ] The title and thumbnail promise the same thing.
- [ ] The first 30 seconds pays that promise.
- [ ] The video is the length the format promises; no padding.
- [ ] Audio is clean, levelled and consistent.
- [ ] Captions are accurate; names and numbers are right.
- [ ] No unlicensed music, images or footage.
- [ ] Numbers are sourced or labelled as estimates.
- [ ] Description has chapters, links and the channel CTA.
- [ ] Privacy is explicit; public has the owner's yes.
- [ ] The upload is registered with Amplifier and the slate row is updated.

A failed gate is not a request to "polish later". Fix it or do not publish.

## 9. Escalation to the owner

Only three things go to the owner as asks:

1. **Money** — a paid tool, a freelancer, ads, a licence.
2. **Access** — a channel reconnect, a brand account, a copyright claim.
3. **A public commitment** — a series promise, a collab, a sponsor, a face reveal.

Everything else is the CEO's job. Do not escalate a title choice or a thumbnail
colour as if it were a board decision.

## 10. Anti-patterns

- **Reporting without deciding.** A weekly review that ends with "here are the
  numbers" is a newsletter, not management.
- **Starting a fifth channel to avoid fixing the four.** Novelty is the most
  expensive form of procrastination.
- **Changing the topic when the packaging is the problem.** If the video reached
  nobody, the title/thumbnail failed before the content did.
- **Publishing more instead of better.** Volume is a scale tactic, not a fix.
- **Judging a channel on a 10-view sample.** Read the trend, the packaging and the
  first 30 seconds. Do not overfit noise.
- **Letting a channel rot silently.** Park it on a date or ship it. "Soon" is not
  a status.
- **Letting the builder publish.** The gate exists because the builder is optimising
  for the video, not the portfolio.
- **Measuring subscribers before reach.** On a small channel, subs are a lagging
  indicator of packaging, not a growth lever.

## 11. Keeping the ledger honest

- Sync at least weekly, ideally Monday. A stale ledger is worse than no ledger
  because it invites confident wrong calls.
- Every manual status change gets a note: why the channel is paused, why the
  cadence changed, why the tier is locked.
- Close decisions with an outcome. A decision log without outcomes is a diary.
- Review parked channels at the restart date, not when you happen to remember.
- If the Analytics API is off, say so in every review. Do not let a data gap turn
  into a fabricated story.

## 12. The one-sentence test

At the end of a review, the CEO should be able to say:

> "This week we are betting on **X**, fixing **Y**, and deliberately ignoring
> **Z**, because **evidence**."

If that sentence cannot be said, the review is not done.
