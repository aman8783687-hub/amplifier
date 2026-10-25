# Printing Life — Publishing and Growth

Publishing is part of the format. A great episode with a weak title, thumbnail or
first 30 seconds is a failed episode.

---

## 1. Channel identity

| Element | Value |
|---|---|
| Name | **Printing Life** |
| YouTube ID | `UC80bd4q0gfzpzZlMLva4h4g` |
| Amplifier channel ID | `6ad8b9fd493e3f65823b402b` |
| Promise | History's biggest messes, explained like a cartoon — and the ordinary things that quietly changed the world. |
| Tone | Deadpan, curious, PG-13, never sneering at the past |
| Cadence | One episode every 2–3 weeks; never rush a tentpole |
| Playlists | `Small Wars`, `Profiles`, `Origins`, `Main Stories` |

### About text (draft)

> History is a series of reasonable people making catastrophic decisions.
> Printing Life explains the wars, revolutions and inventions that rearranged
> the world — with cartoons, maps and an unhealthy interest in paperwork.
>
> New episodes every few weeks. Start with a Small War.

### Banner

- Parchment background, a crowd of simplified characters, one red banner with
  the channel name.
- No episode-specific text. No "new video every Friday" promise unless it is
  true.

### Pinned comment

> Which disaster should we explain next? Drop it below. Sources for this episode
> are in the description.

---

## 2. Titles

Use the canonical name. See `topics-and-titles.md` for the full rules.

```
The Pastry War - Small Wars #1
The Printing Press - Printing Life
The Haitian Revolution - Printing Life (Part 1)
```

- Front-load the noun.
- Keep the part before `|` under 60 characters.
- No question titles, no all-caps, no fake stakes.
- `(Part 1)` only when Part 2 exists or is already scripted.

---

## 3. Thumbnail

One idea, one threat, one title.

- 1280×720, under 2 MB, JPG or PNG.
- 2–4 word title, Anton, gold fill, heavy ink stroke.
- One or two characters, large, with a clear emotion.
- Background is the most dramatic scene plate, darkened at the edges.
- `PART 1` badge only for two-parters.
- `Printing Life` logo bottom-right.
- Squint test at 320×180: the conflict and the title must still read.

Do not put the full episode title on the thumbnail. The thumbnail is a poster,
not a label.

---

## 4. Description

```text
In 1838, a French pastry chef in Mexico City claimed some Mexican officers
had eaten his cakes and refused to pay. France sent a fleet. Mexico got a war.
This is the story of the smallest bill in history — and the leg it cost.

CHAPTERS
00:00 A pastry problem
01:12 The bill
03:40 The fleet arrives
06:05 Santa Anna's leg
08:20 What it actually changed

SOURCES
- [Author, Title, year, pages]
- [Archive / museum / primary source]
- [Second source for the main claim]

MUSIC
"Track" by Artist — licensed under CC-BY 4.0 (source URL)

Made with maps, ink and an unreasonable amount of coffee.
#history #pastrywar #animatedhistory
```

Rules:

- First two lines must work as a search snippet and a hook.
- Chapters start at `00:00` and have at least three chapters.
- Every factual claim that carries the story gets a source in the description.
- Credit every CC-BY track. No credit, no track.
- 3–5 hashtags, not 15.

### Chapters

YouTube requires:

- the first chapter at `00:00`;
- at least three chapters;
- each chapter at least 10 seconds long.

Keep chapter names short and curious. Do not name them "Introduction",
"Part 1", "Conclusion".

---

## 5. Tags

15–25 tags, three layers:

| Layer | Examples |
|---|---|
| Broad | history, animated history, history explained |
| Topic | pastry war, franco-mexican war, 1838, santa anna |
| Intent | history documentary, history animation, funny history |

Do not use competitor channel names as tags. Do not stuff unrelated trending
topics. Tags are a minor ranking signal; the title and thumbnail do the work.

---

## 6. Upload

The Amplifier bridge uploads to **one** channel: Printing Life. It mints a
short-lived YouTube token, streams the file, sets the thumbnail, and registers
the video for analytics.

```bash
cd <episode-workdir>
SKILL=~/.claude/skills/printing-life-yt-skill

# 1. validate channel, key and metadata without uploading
python3 "$SKILL/scripts/upload_to_amplifier.py" \
  --video final/episode.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Printing Life" \
  --dry-run

# 2. upload as private for review
python3 "$SKILL/scripts/upload_to_amplifier.py" \
  --video final/episode.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Printing Life"

# 3. when approved, publish
python3 "$SKILL/scripts/upload_to_amplifier.py" \
  --video final/episode.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Printing Life" \
  --privacy public
```

Metadata file format:

```text
Title: The Pastry War - Small Wars #1
Description:
<full description with chapters and sources>
Tags: history, animated history, pastry war, franco-mexican war, santa anna
Privacy: private
```

Notes:

- Default privacy is **private**. Never publish without the owner's explicit
  approval.
- Do not fan out to every connected channel. Only Printing Life receives the
  video.
- Never print or commit the Amplifier agent key.
- The upload script validates the channel by title and fails loudly if it is
  missing.

---

## 7. Pre-publish checklist

### Story

- [ ] The first 30 seconds contain a person, a problem and a promise.
- [ ] The episode has a turn the viewer does not expect.
- [ ] The ending says what changed and who paid.
- [ ] No invented quotes, numbers or sources.
- [ ] Sensitive scenes handled without graphic imagery or jokes at victims.

### Picture

- [ ] Every scene is 1920×1080, no letterbox seams.
- [ ] No baked text, letters or numbers in any generated image.
- [ ] Character costumes and faces are consistent.
- [ ] No frame holds longer than 15 seconds without a move or cut.
- [ ] Cards, lower thirds and impacts do not overlap each other.
- [ ] Bottom 18% is clean where lower thirds appear.

### Sound

- [ ] Every line is audible on phone speakers.
- [ ] Music ducks under narration and is credited.
- [ ] No gap longer than 0.6 s inside a scene.
- [ ] Final is −14 LUFS, −1.5 dBTP, stereo 48 kHz.
- [ ] Captions generated and checked.

### Packaging

- [ ] Title follows the canonical pattern.
- [ ] Thumbnail passes the squint test.
- [ ] Description has hook, chapters, sources, music credit.
- [ ] Tags are relevant and not competitor names.
- [ ] End screen points to one video, not five.

---

## 8. First 24 hours

1. Publish as **private**, watch the whole thing once on a phone.
2. Fix any audio or timing issue before making it public.
3. Publish, then pin the source/next-topic comment.
4. Add the video to the correct playlist.
5. Set the end screen to the strongest related episode.
6. Do not edit the title or thumbnail for at least 48 hours. Give the test a
   chance.
7. Note the first-day CTR and average view duration in the ledger.

---

## 9. Analytics

```bash
python3 ~/.claude/skills/printing-life-yt-skill/scripts/amplifier_analytics.py \
  --channel "Printing Life" --range 28d

# one video (Amplifier videoId from the upload output)
python3 .../amplifier_analytics.py --video <id> --range 28d

# force a fresh pull from YouTube first
python3 .../amplifier_analytics.py --channel "Printing Life" --refresh
```

Read in this order:

1. **Impressions CTR** — is the packaging working? Below ~3% on a new channel is
   a packaging problem, not a topic problem.
2. **Average view duration / percentage** — is the story holding? A drop in the
   first 30 seconds is a cold-open problem. A drop at 40% is a mid-episode
   problem.
3. **Views per impression by traffic source** — browse vs search tells you
   whether the thumbnail or the title is doing the work.
4. **Subscribers per 1,000 views** — are they coming back?
5. **Comments** — are people asking for the next topic or correcting a fact? Both
   are useful; one is urgent.

Do not overreact to the first 48 hours. Judge at **10 videos** or **90 days**,
whichever comes first.

---

## 10. Experiment rules

Test one variable at a time:

- **Thumbnail A/B:** same title, two images. Change after 72 hours, not 6.
- **Title A/B:** same thumbnail, canonical vs curiosity angle. Only for Small
  Wars; never for main stories.
- **Cold open A/B:** two scripts for the same topic, 30 seconds each, read them
  aloud. Pick the one a friend understands without context.

Never test:
- two different topics at once;
- a new visual style mid-series;
- a new narrator voice mid-series;
- clickbait that the episode does not pay off.

---

## 11. Cleanup after upload

After a verified upload:

```bash
python3 ~/.claude/skills/printing-life-yt-skill/scripts/cleanup_after_upload.py \
  --workdir . \
  --video-id <youtubeVideoId> \
  --title "<episode title>" \
  --yes
```

It keeps the thumbnail, script, metadata, captions and a small `uploaded.json`
record, and deletes the heavy frames, clips, audio and masters. Run with
`--dry-run` first if you are unsure.
