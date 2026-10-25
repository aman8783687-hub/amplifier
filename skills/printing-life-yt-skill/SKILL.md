---
name: Printing Life YouTube Video Builder
description: End-to-end builder for Printing Life (English history YouTube channel) videos in a flat 2D cartoon, OverSimplified-inspired style. Use for ANY task on this channel — topic research, episode script, British deadpan narration with multiple character voices, Perchance scene plates, parchment maps, title/chapter cards, speech bubbles, impact words, camera moves, SFX, music bed, thumbnail, title/description/chapters/tags, upload to the authenticated Printing Life channel via Amplifier, post-upload cleanup, or analytics. Trigger even for one slice ("pick the next topic", "write the Pastry War script", "redo the thumbnail", "upload this episode"). Do NOT start a full video unless the user explicitly asks for one.
---

# Printing Life — YouTube Video Builder

Builds a complete, upload-ready history episode in the channel's visual language:
flat 2D cartoon, thick ink outlines, oversized heads, parchment maps, deadpan
British narration, sharp comic timing.

**Do not produce a video until the user asks.** Topic lists, scripts, style
tests, thumbnails and research are all valid standalone requests.

---

## The channel (locked)

| Element | Value |
|---|---|
| Channel | **Printing Life** |
| YouTube ID | `UC80bd4q0gfzpzZlMLva4h4g` |
| Amplifier ID | `6ad8b9fd493e3f65823b402b` |
| Amplifier status | connected, verified 2026-10-22 |
| Promise | History's biggest messes, explained like a cartoon — plus the ordinary inventions that quietly changed the world |
| Format | 6–16 min, 16:9, 1920×1080, one story per episode |
| Look | Flat 2D comic history: ink outlines, parchment, brick red, navy, mustard, olive |
| Voice | edge-tts `en-GB-RyanNeural`, deadpan; up to four character voices |
| Music | licensed beds, ducked under narration; no track without a licence |
| Captions | clean SRT; no burned karaoke captions |
| Upload | one channel only: Printing Life. Default private |

The channel currently has one upload in a different format ("Your Life as Every
Level of a Fake ID Scammer"). It is not the template for this skill. Leave it as
an early experiment or unlist it when the new slate begins; do not build the new
identity around it.

### Relationship to OverSimplified

The channel uses the *visual and structural grammar* popularised by
OverSimplified: flat cartoon history, comic cold opens, maps, chapter cards,
deadpan narration, two-part epics and tiny-wars. It must not use their actual
art, characters, logo, music, scripts, thumbnails or series names. Build original
characters from the cast bible, original cards, original music choices and
original jokes.

---

## Non-negotiables

1. **Facts are real.** Simplified structure, never invented facts, quotes or
   numbers. Two sources per major claim in `research.md`.
2. **No text in generated images.** All words are rendered by `make_cards.py`.
   A plate with baked lettering is rejected and regenerated.
3. **One action per image.** One subject, one verb, one or two props.
4. **Bottom 18% stays calm** for lower thirds.
5. **No background music over the voice.** Music is ducked; if it fights the
   narration, lower it or cut it.
6. **No atrocity punchlines.** PG-13. Explain the harm; never score a joke off
   victims.
7. **No fake urgency or clickbait.** The episode must pay off the thumbnail.
8. **Upload only to Printing Life**, and only public when the owner says so.
9. **Never print or commit the Amplifier agent key.**
10. **Do not clone protected assets.** Style is a language, not a licence.

---

## Pipeline at a glance

```
topic + research
  → script.md              (one file, the source of truth)
  → voice.py               (multi-voice narration + timeline + captions)
  → gen_images.py          (Perchance scene plates)
  → prep_frames.py         (cover-crop to 1920×1080)
  → make_cards.py          (title, chapters, lower thirds, impacts, bubbles)
  → make_sfx.py            (local SFX palette)
  → assemble.py            (camera moves, overlays, SFX, music, loudness)
  → make_cards.py thumbnail
  → metadata + dry-run + upload
  → cleanup_after_upload.py
  → amplifier_analytics.py
```

Everything reads the same `script.md`. Do not maintain a second copy of the
narration.

---

## Step 0 — Topic and research

Pick from `references/topics-and-titles.md`. For a new channel, start with a
**Small War** or an **Origin**, not a 40-minute epic.

Write `research.md` in the episode folder:

- the one-sentence story;
- why it mattered (the consequence);
- 3–6 cast members, each with one want and one flaw;
- only the dates that will appear on screen;
- five visual set pieces;
- the twist;
- the bill (what changed, who paid);
- two sources per major claim;
- sensitive material and how it is handled.

If a claim has no source, it does not go in the script.

---

## Step 1 — Script

Create the episode folder and copy the template:

```bash
EP=~/development/printing_life_yt/episodes/pastry-war
mkdir -p "$EP"
cp ~/.claude/skills/printing-life-yt-skill/templates/script-template.md "$EP/script.md"
```

Target length:

| Runtime | Words | Scenes |
|---|---:|---:|
| 7 min | 1,050 | 45–52 |
| 10 min | 1,500 | 62–75 |
| 12 min | 1,800 | 75–90 |
| 15 min | 2,250 | 90–110 |

A scene is one image, one camera move, 7–12 seconds. If a scene runs 20 seconds,
add a cutaway.

### Script header

```markdown
# TITLE: The Pastry War
# SLUG: pastry-war
# PART:
# STYLE: tintin

# VOICE NARRATOR: en-GB-RyanNeural | +0% | +0Hz
# VOICE CHEF: en-GB-RyanNeural | +8% | +18Hz
# VOICE OFFICER: en-GB-ThomasNeural | -4% | -15Hz

# CAST CHEF: a small round French pastry chef with a tall white toque, a curled
# black moustache, a flour-dusted apron and tiny dot eyes
# CAST OFFICER: a tall Mexican officer in a dark blue 1830s uniform with gold
# epaulettes, a high collar and a very flat expression
```

- `VOICE` names become speaker keys. Every speaker in the body must have one.
- `CAST` is the character bible. Use `{NAME}` tokens in `IMG:` prompts and
  `gen_images.py` substitutes the full description. This is how consistency
  survives a model with no memory.
- `STYLE` is `tintin` (default), `comic` or `flat`.

### Scene header

```markdown
## s04 | scene | The fleet
```

`id | kind | title`. Kinds: `title`, `chapter`, `scene`, `outro`. The id is used
for every filename.

### Directives

| Directive | Meaning |
|---|---|
| `IMG: ...` | Image prompt, one action, no text |
| `CARD: MAIN \| SUB` | Render a title/chapter card instead of a generated plate |
| `DUR: 3.0` | Minimum scene duration (for silent cards) |
| `MOVE: in` | `in`, `out`, `left`, `right`, `up`, `down`, `shake`, `none` |
| `ZOOM: 1.18` | Maximum push-in (default 1.18) |
| `LOWER: TEXT \| at \| dur` | Lower third, seconds relative to scene |
| `BUBBLE: SPEAKER \| x,y` | Speech bubble on that speaker's line (0–1 coords) |
| `IMPACT: TEXT \| at \| dur` | Slamming keyword with starburst |
| `SFX: name \| at \| gain` | `whoosh`, `boom`, `thud`, `pop`, `ding`, `sting`, `riser`, `scratch`, `stamp` |
| `ARROW: x1,y1,x2,y2 \| at \| dur` | Map arrow, normalized coords |
| `MUSIC: track.mp3 \| gain` | Start a music cue at this scene |
| `NOTE: ...` | Author note, ignored by the pipeline |

Dialogue is `SPEAKER: text`. Keep lines short. Write numbers as words.

### Scene pattern

A good scene has:

1. one image prompt with a clear action;
2. one camera move;
3. 1–3 narration lines;
4. at most one punctuation layer (impact, bubble, arrow or lower third).

Do not stack an impact, a bubble, an arrow and a lower third on the same beat.

### Structure

Follow `references/episode-format.md`:

- cold open (0–6%);
- title card;
- the world;
- the fuse;
- act turn;
- the mess;
- midpoint reversal;
- the cost;
- the turn;
- the bill.

Chapter cards every 2–3 minutes. Hard cuts. Hold reactions for 1.2–2 s after a
punchline.

---

## Step 2 — Voice

```bash
cd "$EP"
python3 ~/.claude/skills/printing-life-yt-skill/scripts/voice.py \
  script.md --workdir . --jobs 3
```

Outputs:

- `audio/lines/s01_00.mp3` — one file per line;
- `audio/s01.wav` — scene audio, gaps inserted;
- `audio/timeline.json` — scene and line timings;
- `captions.srt` — full-episode captions.

Options:

- `--force` re-records everything.
- `--only s03 s04` re-records selected scenes but still builds the full timeline.
- `--reuse` keeps existing MP3s and rebuilds timing offline.
- `--jobs 1` if the service is rate-limiting.

Check the reported runtime before generating images. If it is 20% over target,
cut scenes now.

Edge-tts network failures are covered in `references/audio-and-sfx.md`. Retry,
reduce jobs, update the package, or change network. Never publish a robotic
stand-in voice.

---

## Step 3 — Images

Calibrate the style once per session:

```bash
python3 ~/.claude/skills/printing-life-yt-skill/scripts/gen_images.py \
  script.md --workdir . --only s01 --style tintin --force
```

Then generate all plates:

```bash
env -u PYTHONHOME -u PYTHONPATH python3 \
  ~/.claude/skills/printing-life-yt-skill/scripts/gen_images.py \
  script.md --workdir . --variants 2
```

- Outputs `images2/s01.jpg` and alternatives in `images2/alt/`.
- `images2/prompts.json` records the exact prompt.
- Skips existing plates; `--force` regenerates.
- `--only`, `--start`, `--end` for batches.

Review before cropping:

- no text/letters/numbers;
- correct period costumes;
- character matches the cast bible;
- one clear action;
- bottom 18% calm;
- palette is muted (no neon).

Reroll the bad ones. Two failures means simplify the beat, not keep rolling.

Crop:

```bash
python3 ~/.claude/skills/printing-life-yt-skill/scripts/prep_frames.py \
  --workdir . --src images2 --dst images3 --crop-y 0.2
```

---

## Step 4 — Cards and overlays

`assemble.py` renders overlays automatically from the script. To preview or
override a layer:

```bash
SKILL=~/.claude/skills/printing-life-yt-skill

python3 "$SKILL/scripts/make_cards.py" title "The Pastry War" --part 1 \
  --sub "1838" --out build/cards/title.png

python3 "$SKILL/scripts/make_cards.py" chapter "THE BILL" --sub "1839" \
  --num "II" --out build/cards/ch2.png

python3 "$SKILL/scripts/make_cards.py" lower "MEXICO CITY, 1838" \
  --out build/ov/s02_lower.png

python3 "$SKILL/scripts/make_cards.py" impact "A FLEET" \
  --out build/ov/s04_impact.png
```

Rules:

- No impact or bubble on top of a chapter card. Cards are their own beat.
- Lower thirds sit bottom-left; keep them under 4 seconds.
- One impact word per beat.
- Bubbles point toward the speaker's side of the frame.

---

## Step 5 — SFX

```bash
python3 ~/.claude/skills/printing-life-yt-skill/scripts/make_sfx.py \
  --workdir .
```

Creates nine WAVs in `sfx/`. No licensing, no downloads.

---

## Step 6 — Assemble

Always dry-run first:

```bash
python3 ~/.claude/skills/printing-life-yt-skill/scripts/assemble.py \
  script.md --workdir . --dry-run
```

Render a preview of the first four scenes:

```bash
python3 .../assemble.py script.md --workdir . --preview 4 \
  --out final/preview.mp4
```

Full render:

```bash
python3 .../assemble.py script.md --workdir . --crf 18
```

Output: `final/<slug>.mp4`, 1920×1080, 30 fps, −14 LUFS, stereo 48 kHz.

Music:

```bash
# global bed
python3 .../assemble.py script.md --workdir . \
  --music music/bed.mp3 --music-gain 0.12

# or cues from MUSIC: lines in the script
python3 .../assemble.py script.md --workdir .
```

If no music is available, render without it. Do not fill the silence with a
copyrighted track.

After the render, watch it once at 1× on a phone. Check:

- every scene is the intended duration;
- overlays appear and disappear on time;
- no text is clipped by a push-in;
- SFX are not louder than the voice;
- the final audio does not clip.

---

## Step 7 — Thumbnail

```bash
python3 "$SKILL/scripts/make_cards.py" thumbnail \
  --bg images3/s04.jpg \
  --title "THE PASTRY WAR" \
  --part 1 \
  --kicker "1838" \
  --out final/thumbnail.jpg
```

- 1280×720, under 2 MB.
- 2–4 words, gold fill, heavy ink stroke.
- One or two characters, large, clear emotion.
- Use a **scene plate**, not a chapter card (no duplicate title).
- Squint test at 320×180.

Optional cutouts: `--fg-left character.png --fg-right character.png` (transparent
PNGs).

---

## Step 8 — Metadata

Write `final_upload_metadata.txt` from
`templates/metadata.txt`:

```text
Title: The Pastry War - Small Wars #1
Description:
<hook, chapters, sources, music credit, hashtags>
Tags: history, animated history, pastry war, ...
Privacy: private
```

Chapter rules: first at `00:00`, at least three, each at least 10 seconds.

Title rules: canonical name, front-loaded noun, no questions, no all-caps, no
fake stakes. See `references/publishing.md`.

---

## Step 9 — Upload

The Amplifier bridge is verified for Printing Life.

```bash
SKILL=~/.claude/skills/printing-life-yt-skill

# validate without uploading
python3 "$SKILL/scripts/upload_to_amplifier.py" \
  --video final/pastry-war.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Printing Life" \
  --dry-run

# upload private for review
python3 "$SKILL/scripts/upload_to_amplifier.py" \
  --video final/pastry-war.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Printing Life"
```

Only pass `--privacy public` when the owner has explicitly approved the cut.

The script:

1. finds the channel by title;
2. mints a short-lived YouTube token;
3. streams the file straight to YouTube;
4. sets the thumbnail;
5. registers the upload with Amplifier;
6. prints `youtubeVideoId`, `youtubeUrl`, `amplifierVideoId`.

Default privacy is `private`. Never fan out to other channels.

---

## Step 10 — Cleanup

After a verified upload:

```bash
python3 "$SKILL/scripts/cleanup_after_upload.py" \
  --workdir . \
  --video-id <youtubeVideoId> \
  --title "<episode title>" \
  --yes
```

It keeps `final/thumbnail.jpg`, `script.md`, `metadata`, `captions.srt` and
`uploaded.json`, and deletes the heavy frames, clips, audio and masters. Run
`--dry-run` first if unsure.

---

## Step 11 — Analytics

```bash
python3 "$SKILL/scripts/amplifier_analytics.py" \
  --channel "Printing Life" --range 28d
```

- one video: `--video <amplifierVideoId>`;
- whole account: `--overview`;
- fresh pull: add `--refresh`.

Report totals and per-video numbers, not raw JSON. Read CTR first, then average
view duration, then subscribers per 1,000 views. Judge the channel at 10 videos
or 90 days.

---

## Quality gates

An episode does not upload until all are true:

**Story**
- [ ] Cold open has a person, a problem and a promise in 30 s.
- [ ] There is a turn the viewer does not expect.
- [ ] The ending says what changed and who paid.
- [ ] No invented facts, quotes, numbers or sources.
- [ ] Sensitive material is handled without graphic imagery or victim jokes.

**Picture**
- [ ] 1920×1080, no letterbox seams.
- [ ] No baked text in any generated image.
- [ ] Cast costumes and faces are consistent.
- [ ] No frame holds >15 s without a move or cut.
- [ ] Cards, lower thirds, impacts and bubbles do not collide.
- [ ] Every push-in leaves faces and text inside the safe area.

**Sound**
- [ ] Every word is audible on a phone speaker.
- [ ] Music is licensed, credited and ducked.
- [ ] No gap >0.6 s inside a scene.
- [ ] −14 LUFS, −1.5 dBTP, stereo 48 kHz.
- [ ] Captions generated and proofread.

**Packaging**
- [ ] Title follows the canonical pattern.
- [ ] Thumbnail passes the squint test.
- [ ] Description has hook, chapters, sources and music credit.
- [ ] Tags are relevant, no competitor names.
- [ ] End screen points to one related episode.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| edge-tts websocket timeout | Retry with `--jobs 1`; update edge-tts; change network/VPN |
| A line is missing from audio | Re-run `voice.py --only <scene>` |
| Scene duration is wrong | Re-run `voice.py --reuse`; check `DUR:`; check timeline |
| Image has text | Reroll; remove "map labels/newspaper/book cover" wording; add negative |
| Character changes between scenes | Use `{NAME}` tokens; do not paraphrase the cast header |
| Zoom crops a face | Lower `ZOOM:` to 1.08 or use `MOVE: none` |
| Overlay appears late | Check `at` is relative to the scene, not the episode |
| Bubble is missing | `BUBBLE:` must name a speaker that exists in that scene |
| Arrow covers a face | Choose empty coords; arrows are static with a fade |
| Music drowns the voice | Lower `--music-gain` to 0.08; do not raise compression |
| Concat has a click | Per-clip AAC priming; re-encode the final audio (assemble does) |
| Upload says channel not found | Check `GET /api/channels`; the title must match "Printing Life" |

---

## Bundled files

```
printing-life-yt-skill/
  SKILL.md
  references/
    style-guide.md           visual bible, prompts, palette, motion, thumbnail
    episode-format.md        beats, cold opens, two-parters, humour, accuracy
    topics-and-titles.md     lanes, 35+ topics, title rules, first ten
    audio-and-sfx.md         voices, music licensing, SFX, mix targets
    publishing.md            channel identity, metadata, upload, analytics
  scripts/
    plib.py                  script parser, palette, fonts
    voice.py                 multi-voice edge-tts + timeline + captions
    gen_images.py            Perchance plates, style presets, cast tokens
    prep_frames.py           cover-crop to 1920×1080
    make_cards.py            title/chapter/lower/impact/bubble/thumbnail/arrow
    make_sfx.py              nine synthesized SFX
    assemble.py              camera moves, overlays, concat, music, loudness
    upload_to_amplifier.py   upload to Printing Life
    amplifier_analytics.py   channel/video analytics
    cleanup_after_upload.py  reclaim disk after upload
  assets/fonts/              Anton, Bebas Neue, Luckiest Guy (OFL/Apache)
  templates/
    script-template.md       parseable episode skeleton
    metadata.txt             upload metadata skeleton
```

---

## First-run checklist

Before the first real episode:

1. Run the style calibration (`tintin` / `comic` / `flat`) and lock one.
2. Generate one character sheet per lead; write the descriptors into `# CAST`.
3. Render a 4-scene preview (`--preview 4`) and watch it on a phone.
4. Confirm the Amplifier dry-run prints `Printing Life` and `tokenMinted: true`.
5. Write `research.md` before the first line of narration.
6. Pick the first topic from the Small Wars or Origins lane, not a WW2 epic.
