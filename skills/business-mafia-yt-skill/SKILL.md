---
name: business-mafia-yt-skill
description: 'End-to-end builder for Business Mafia (Hindi YouTube channel) videos — 8-12 minute 16:9 stickman story videos about how everyday Indian businesses actually make money and how the viewer could start one (chai wala, gym, dhaba, dumper, politician...). Use for ANY task on this channel: topic, research, Hindi script, narration, scenes, captions, assembly, thumbnail, SEO metadata, sound effects, upload to the authenticated Business Mafia channel, post-upload disk cleanup, or analytics. Trigger even for one slice ("aaj ki script likho", "redo the thumbnail", "upload this episode").'
---

# Business Mafia — YouTube Video Builder

Builds a complete, upload-ready Hindi YouTube video from a topic. "Mafia" is a
metaphor for the insider's playbook: the channel never glorifies crime and never
teaches fraud. One video per run, uploaded to the single authenticated channel
**Business Mafia**.

Pipeline:

1. **Topic** — a boring, hyper-local Indian cash business with a myth the hisaab overturns.
2. **Script** — Hindi story, 8-12 min, five tags `[HOOK] [DUNIYA] [KHEL] [RAAZ] [SABAK]`.
3. **Voice** — Edge-TTS `hi-IN-MadhurNeural`, per-section rate/pitch presets, then **trim the dead air**.
4. **Images** — Perchance AI, black-marker stickman on a white whiteboard.
5. **Subtitles** — ASS Devanagari captions, word-by-word pop, gold highlight.
6. **Dynamic edit** — full-bleed 16:9 frames, Ken Burns zoom + fade-in per scene.
7. **Overlays** — optional real photos/memes, centered, fade in/out.
8. **SFX** — synthesized whoosh on section cuts, ding on money reveals, sting on `[RAAZ]`, **no music**.
9. **Final** — concat, master to -14 LUFS, stereo, 1080p.
10. **SEO** — pull real YouTube autocomplete queries, then write title/description/tags.
11. **Upload** — publish to the authenticated **Business Mafia** channel via the Amplifier bridge.
12. **Cleanup** — after a verified upload, delete the frames, clips, audio and master to reclaim disk.
13. **Analytics** — read per-video and channel stats back from Amplifier.

## The brand (locked)

| Element | Locked value |
|---|---|
| Channel | **Business Mafia** (YouTube `UCcm8EqvJwq9WfPdDJG06f1g`, connected in Amplifier) |
| Host | **The Boss** stickman: black fedora with a gold band, thin black suit-jacket outline, small solid gold tie, two black dot eyes, **no mouth**, calm knowing face |
| Palette | Black, white, gold `#D4A017`. Gold is the accent and the colour of money. **No red**, no other colour |
| Art | Hand-drawn ink on a clean white whiteboard. Three switchable presets: `boss` (default marker stickman), `xiaohei` (sparse editorial ink, black creature), `qhuman` (natural-skin Q-version people). See **Visual style presets**. No text/letters/numbers in the image |
| Voice | edge-tts `hi-IN-MadhurNeural` (male, insider tone); fallback `hi-IN-SwaraNeural` only after logging |
| Language | Conversational Hindi in Devanagari, the way people talk at a chai stall. English business words stay English but in Devanagari (प्रॉफ़िट, मार्जिन, कस्टमर) |
| Numbers | Spoken as words ("दस रुपये", "पचास हज़ार"), never digits in narration; digits are fine in the title/thumbnail |
| Runtime | 480-720 s (8-12 min). **18-22 Hindi words per beat = 8-9 s.** 60-75 beats / 1,100-1,450 words ≈ 8-10 min. 85 short beats of ~11 words gave only 6:35 — count words, not beats |
| Formats | `kamai` deep dive ("<X> वाला कितना कमाता है?") and `list` ("₹<X> से शुरू करें ये <N> बिज़नेस"), **alternated** |
| Aspect | 16:9, 1920x1080, **full-bleed** (Perchance renders 768x512; cover-crop with `prep_frames.py`, never pad) |
| Captions | Noto Sans Devanagari Bold **74**, **3 words** per chunk, gold highlight `&H0017A0D4`, outline 6 + shadow 2.2, marginV 105 |
| Audio | -14 LUFS, stereo 48 kHz. **No pause longer than 0.45 s** in the finished file; whoosh on section cuts, ding on money reveals, sting on `[RAAZ]`, **no background music** |
| Thumbnail | Two brush bands left (white on black / black on yellow), money digits highlighted, green growth arrow top right, boss large on the right with gold money, optional green rupee badge |
| Vibe | "यार, ये तो इज़्ज़त का धंधा है, और समझदारी से किया जाए तो मैं भी कर सकता हूँ।" |

## Visual style presets (hand-drawn explainer)

The look is adapted from **hi-nikola/hand-drawn-explainer-video-nikola**
(Apache-2.0). Its "Xiaohei" preset is in turn credited to Ian
(`helloianneo/ian-xiaohei-illustrations`). We borrow the drawing language, not
the Chinese-language pipeline.

Three presets, one per episode (pick once in the shotlist, never mix inside a
video). Set `STYLE_PRESET` for `gen_images.py`:

| Preset | Use it for | Look |
|---|---|---|
| `boss` (default) | Every business story; the channel's signature | Thick black marker stickman, black fedora + gold band, suit outline, gold tie, white whiteboard, one or two props |
| `xiaohei` | Abstract/explainer beats: "how margin works", "where the money leaks", system and methodology episodes | Pure white or warm off-white, ~35%+ negative space, sparse slightly wobbly black ink, flat solid black shapes, tiny **white dot eyes**, one absurd-but-explanatory core action, very low line density |
| `qhuman` | Character-led episodes where the owner's age/outfit matters (a 60-year-old dhaba owner, a young delivery kid) | Soft natural-skin Q-version cartoon human, clear age and outfit anchors, rounded shapes, still simple and low-detail |

### Rules shared by all three

- **One action per image.** One subject, one verb, one or two props. No collages,
  no icon grids, no sticky-note walls.
- **Low line density.** No pencil noise, cross-hatching, dense texture, shading,
  gradients or glossy 3D. Detail is not a quality signal; simplification draws
  better and reads better at phone size.
- **~35% empty space** minimum, and the **bottom 18% stays clean** for captions.
- **No text, letters, numbers, logos or pseudo-writing** in the image. Keywords,
  rupee figures and titles are deterministic ASS/thumbnail text layers, never
  left to the image model.
- **Palette stays black / white / gold.** The upstream Xiaohei preset uses red,
  orange and blue annotation marks; we replace them with gold
  (`#D4A017`) arrows, circles and stickers. No red. `qhuman` may use natural
  skin tone for faces (not an accent colour) with black/white/gold clothing.
- **The Boss keeps his identity in every preset:** black fedora with a gold
  band, small gold tie, two dot eyes, **no mouth**. In `xiaohei` he is a small
  black creature with white dot eyes wearing the same hat and tie.
- **No real-person likeness.** `qhuman` is still a cartoon character, never a
  portrait of a living person.
- If a beat needs a precise keyword, draw the area empty and let the caption
  layer own the word.

### Composition structures

Same drawing style, three ways to arrange a beat:

1. **Single scene** (default) — one act filling the 16:9 frame.
2. **Multi-act story** — one separate scene per beat, each starting from a clean
   whiteboard. This is what the pipeline already does.
3. **Left/right semantic islands** — for a cause→effect, problem→answer or
   before→after beat in a single narration line: left island and right island,
   a **6–10% clean vertical gutter** between them, no ground line, wire, table
   edge, shadow or arrow crossing the gutter. Set `COMPOSITION=islands`.
   On screen the caption carries the "then" — the image does not need an arrow.
   Use it only when both halves deserve ~3 s of screen time; otherwise split
   into two beats.

### Drawability check (before generating)

Ask for every beat: can this be drawn with about 20 strokes? If it needs a
crowd's faces, circuit-board pins, a wood-grain texture, a book's small text, a
phone screen or repeated decorative lines, simplify the beat (one prop, the Boss
alone) or split it. A beat that stays busy after three rerolls is a script
problem, not an image problem.

## Inputs needed
- Topic (e.g., "चाय वाला असल में कितना कमाता है?")
- Format: `kamai` or `list` (alternate; never two of the same in a row)
- Optional: specific meme/photo overlays, thumbnail badge figure, title alternates.

## Topic rules

Only **boring, hyper-local, cash businesses from Bharat** — the ones every
Indian passes daily, where everyone has a guess and nobody has a good video.
The test: is there a myth that simple hisaab overturns, and does the real hisaab
make the owner look smart and hardworking?

Verticals (one per YouTube playlist, never two episodes in a row from the same):
1. **Farming & Pashu** — poultry, mushroom, fish, dairy, goat, bee-keeping.
2. **Transport & Heavy Vehicles** — dumper/tipper, truck, JCB, tractor rental, school van, e-rickshaw.
3. **Khana & Street Food** — chai, momo, pani puri, dhaba, juice, sweet shop, restaurant.
4. **Dukaan & Retail** — kirana, petrol pump, medical store, hardware, jeweller.
5. **Services** — barber, laundry, gym, tent house, mobile repair, wedding planner.
6. **Recycling & Small Industry** — kabadiwala, plastic recycling, cold storage, atta chakki, brick kiln.
7. **Neta & System** — the politician episode only (legal income), not before episode 10.

Never queue apps, finance concepts, sports leagues, luxury or government
systems: those flopped (under 2K views) — keep at least one of every three
episodes in Farming or Heavy Vehicles. *(The 720K/241K/62K figures previously
quoted here were not reproducible from the public channel; re-check actual view
counts in Studio before citing them as evidence.)*

## Step 1 — Script

Write in `script.md` with the five tags, one beat per scene:

```
# चाय वाला असल में कितना कमाता है
Target runtime: 10:00

[HOOK]
1. दस रुपये की चाय बेचने वाला कितना कमाता है? जवाब सुनकर आप उसे इज़्ज़त से देखेंगे।
2. बनाने में लगते हैं लगभग तीन रुपये। और समझदार चाय वाले की असली कमाई एक और चीज़ से होती है। वो राज़ आख़िर में।

[DUNIYA]
...
[KHEL]
...
[RAAZ]
...
[SABAK]
...
```

Structure:
- **`[HOOK]`** (0:00-0:30) — the question everyone has wondered, one surprising rupee number, then tease the owner's smart move ("वो आख़िर में").
- **`[DUNIYA]`** (0:30-2:00) — "मान लीजिए रमेश..." (a hypothetical owner, never a real person): what he invests, where, why, his first month.
- **`[KHEL]`** (2:00-6:30) — where the money comes from, then four or five named costs (EMI, rent, staff, bijli, diesel, wastage, udhaar), each a small scene with रमेश, one rupee number, and **his fix in the same beat**. End with the month's hisaab as a range.
- **`[RAAZ]`** (6:30-8:00) — the one non-obvious thing good owners do; slow down, pay off the hook's tease.
- **`[SABAK]`** (last 1:30-2:30) — "आप शुरू करना चाहें तो": starting cost range, first step, the beginner's mistake, two or three rules, a line of respect, one comment question, next episode, subscribe once.

`list` format: five to seven businesses from the verticals, each with what the
budget buys, how the first customers come, a monthly range as an estimate, and
one beginner mistake + fix. Tease idea #4 and #6 in the hook, pay off in `[RAAZ]`.

Tone rules (hard):
- **Admire, don't expose.** The owner is smart and hardworking, never a victim, never a cheat.
- **Every cost comes with its fix** in the same beat. A cost is never a dead end.
- **No doom words** in hook/`[RAAZ]`/ending: डूबना, बर्बाद, जाल, धोखा, फँस गया.
- **No get-rich promise.** Estimates are said as estimates ("अंदाज़न", "लगभग").
- No filler ("नमस्कार दोस्तों", "आज के इस वीडियो में"), no channel intro.
- Second person, present tense; short sentences; a three-word line after a long one lands hard.
- No formulas, tables, percentages or on-screen math.

Save narration per beat/scene to `audio/seg01.txt` ... `audio/segNN.txt`
(two or three sentences, **18-22 Hindi words**, 8-9 s spoken).

**Budget by words, not by beats.** Measured on the biryani episode: 926 words at
the -8/-12% presets → **6:35** after trimming (141 wpm). So:

| Target | Words | Beats |
|---|---|---|
| 8:00 | ~1,130 | 55-62 |
| 10:00 | ~1,410 | 65-75 |
| 12:00 | ~1,700 | 75-85 |

Eleven-word beats are the #1 reason a "10-minute script" renders at 6:35. If you
want length, write longer beats (one image can hold 8-9 s), not more images.

Never invent numbers or sources. Every rupee figure, date and "first" claim
traces to research, or is said as an estimate with a round range.

## Step 2 — Voice (then kill the dead air)

Section presets (edge-tts rate/volume/pitch). These are the values that sounded
right on the biryani episode: calmer than 1x, because at 1x Madhur runs ~200 wpm
and reads as rushed once the silences are gone.

| Tag | rate | volume | pitch | feel |
|---|---|---|---|---|
| `hook` | -12% | +0% | -2Hz | The rupee shock. Slow, weighty. |
| `duniya` | -8% | +0% | +0Hz | The world and the character. |
| `khel` | -2% | +3% | +0Hz | The money game. Keeps moving. |
| `raaz` | -12% | +0% | -2Hz | The owner's move. Slower, admiring. |
| `sabak` | -12% | -2% | -2Hz | Warm and calm. |

Replace sentence-ending ". " with ", " for the TTS, then synthesize each beat:

```bash
cd <workdir>
for i in $(seq -w 1 N); do
  n="seg$(printf '%02d' $i)"
  text=$(sed 's/\. /, /g' "audio/$n.txt")
  uvx edge-tts --text "$text" --write-media "audio/$n.mp3" \
    --write-subtitles "audio/$n.srt" --voice hi-IN-MadhurNeural \
    --rate=-8% --volume=+0% --pitch=-1Hz
done
```

### Then trim — this is not optional

edge-tts returns **~0.2 s lead-in and ~1.0-1.5 s trailing silence on every
call**, plus ~1.2 s at every danda (।). Concatenated raw, a 6-minute script
becomes an 8.5-minute video that stalls between every sentence. On the biryani
episode, **154 s of 517 s was silence (30%)** and the human's first note was
"annoying pauses".

```bash
python3 "$SKILL_DIR/scripts/trim_silence.py" --workdir .
# audio/segNN.mp3 + .srt  ->  audio2/segNN.wav + .srt (cue times remapped)
```

Defaults: lead 0.06 s, tail 0.20 s, internal pauses capped at 0.38 s, detection
at -42 dBFS with a 0.20 s floor. The SRT is remapped through the exact cut
points, so captions stay frame-accurate; do not rebuild the SRT by hand.

Check the finished file, not the clips:

```bash
ffmpeg -hide_banner -i final/<name>.mp4 -af "silencedetect=noise=-40dB:d=0.45" -f null - 2>&1 | grep -c silence_start
# must print 0
```

If the trimmed runtime lands under 8:00, **add beats** (18-22 words each) — do
not re-introduce silence.

Hindi pronunciation: numbers as words; English business words in Devanagari; if
a word is mispronounced, respell it phonetically in Devanagari and redo that
segment. Never change voice speed to fix runtime — cut or add beats.

## Step 3 — Images (Perchance)

Use the perchance-image-generation skill. One subject per segment in
`gen_images.py` `SUBJECTS`. The script builds each prompt from
`STYLE_PRESETS[STYLE_PRESET]` + `COMPOSITIONS[COMPOSITION]`:

```bash
# default: boss stickman, one act per frame
env -u PYTHONHOME -u PYTHONPATH python3 gen_images.py 0 N

# sparse black-ink editorial look
STYLE_PRESET=xiaohei env -u PYTHONHOME -u PYTHONPATH python3 gen_images.py 0 N

# natural-skin Q-version people
STYLE_PRESET=qhuman env -u PYTHONHOME -u PYTHONPATH python3 gen_images.py 0 N

# left/right semantic islands (cause → effect beats)
COMPOSITION=islands env -u PYTHONHOME -u PYTHONPATH python3 gen_images.py 0 N
```

Whichever preset, the rules in **Visual style presets** apply: one action per
image, ~35% empty space, bottom 18% clean, black/white/gold, no text, at most
two characters, Boss always on-model (fedora + gold band, gold tie, no mouth).

Reference `boss` prompt:

> hand-drawn black marker stickman on a clean white whiteboard, thick confident
> marker strokes, the stickman wears a black fedora with a gold band, a thin
> black outline suit jacket and a small solid gold tie, exactly two black dot
> eyes and NO mouth, calm neutral face, thin single-line stick limbs, no text,
> no letters, no numbers, one or two simple hand-drawn marker props only, money
> props drawn in gold, no arrows, lots of empty white space, only black, white
> and gold colors, no red, whiteboard explainer animation look

Output to `images2/segXX-*.jpg` (`IMAGES_DIR` overrides).

**At most two characters per shot** (FLUX collapses a third). Write crowded
moments as shot/reverse-shot pairs. Other characters are plain stickmen with one
identifying prop (apron, dumbbell, turban); the Boss is the hat-and-suit host.
**Look at every generated PNG.** Reroll red/extra colours, a mouth, shading,
text, or a wrong character count.

## Step 4 — Animated captions (ASS)

Build per-segment ASS from the (already trimmed) SRT:

```bash
python3 "$SKILL_DIR/scripts/build_ass.py" --workdir . --audio audio2
```

One cue becomes a **3-word chunk**; words appear one at a time and the chunk
clears at the next one. Edit `KEYS` and `MONEY` per topic — highlighting every
business noun turns the whole line gold and destroys the accent.

Locked style: Noto Sans Devanagari Bold **74**, outline **6**, shadow 2.2,
marginV **105**. Thin outlines (3.8) vanish against the Boss's black suit; 6
reads on both white paper and dark art.

**Devanagari shaping:** ffmpeg 6.1's `subtitles`/`ass` filter has **no
`shaping` option** — passing `shaping=complex` fails with "Option not found".
Modern libass already shapes Devanagari correctly by default. Just verify one
frame for a conjunct (क्या, क्ष), the nukta (फ़, ज़) and i-matra placement
before rendering all 85 clips.

## Step 5 — Frame prep + dynamic edit (Ken Burns zoom)

Perchance output is 768x512 (3:2) and **never pure white** (~#FAFAFA with a soft
gradient). Scaling to 1080p and padding onto white leaves a visible rectangular
seam on every cut. Cover-crop instead:

```bash
python3 "$SKILL_DIR/scripts/prep_frames.py" --workdir . --src images2 --dst images3
# 1920x1280 -> crop 1920x1080 with an upward bias so hats are not clipped
```

Then render each clip from the prepped plate:

```bash
for i in $(seq 1 N); do
  n=$(printf "seg%02d" $i)
  z="1.0+0.00055*on"                      # odd beats: zoom in
  [ $((i % 2)) -eq 0 ] && z="1.07-0.00055*on"   # even beats: zoom out
  ffmpeg -y -loop 1 -i "images3/$n.jpg" -i "audio2/$n.wav" \
    -c:v libx264 -preset veryfast -crf 20 -tune stillimage \
    -c:a aac -b:a 192k -ar 48000 -pix_fmt yuv420p -shortest -r 30 \
    -vf "zoompan=z='min(max($z,1.0),1.07)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,subtitles=audio2/$n.ass,fade=t=in:st=0:d=0.2" \
    "clips/$n.mp4"
done
```

Alternating in/out at ~5-7% keeps the cuts from feeling mechanical. No AI
motion (it melts stick figures). Run 3 in parallel (`xargs -P 3`); 85 clips take
6-7 minutes on 4 cores. Verify clip duration matches audio after each encode.

## Step 6 — Overlays (optional, real images/memes)

Source images (Wikimedia Commons `Special:FilePath/...` is copyright-safe;
Imgflip `i.imgflip.com/....jpg` for memes). Download with `curl -sL`. Overlay
centered, larger, with fade — per-clip, not whole-video:

```bash
ffmpeg -y -i clips/segXX.mp4 -loop 1 -i overlay.jpg \
  -filter_complex "[1:v]scale=520:-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1,fade=t=out:st=DUR-0.4:d=0.4:alpha=1[ov];[0:v][ov]overlay=(W-w)/2:(H-h)/2[ovv]" \
  -map "[ovv]" -map 0:a -c:v libx264 -preset fast -crf 20 -c:a copy -shortest clips_ov/segXX.mp4
```

Choose overlay moments at pattern interrupts (surprising facts, new chapters).
Keep on screen 2-8 s. Keep the palette black/white/gold where possible — no red.

## Step 7 — SFX (no music)

Generate the three sounds from scratch — no sample files to ship or lose:

```bash
python3 "$SKILL_DIR/scripts/make_sfx.py" --workdir .
# sfx/whoosh.wav 0.62s · sfx/ding.wav 0.9s · sfx/sting.wav 1.1s
```

Placement (biryani episode, which worked):
- **whoosh** at the start of each section (first beat of HOOK/DUNIYA/KHEL/RAAZ/SABAK), offset -0.18 s so it lands on the cut
- **ding** on the two money reveals — gross per plate and net per plate
- **sting** on the first `[RAAZ]` beat, under the reveal

Mix at ~0.6 peak under the voice; the voice stays untouched. `weights=1 0.3:normalize=0`
or a plain `amix=normalize=0` after normalising the voice. **No background
music, ever.**

## Step 8 — Final concat + master

```bash
# 1. concat the clips (same codec params, so stream copy is safe)
python3 -c "import glob; fs=sorted(glob.glob('clips/seg*.mp4')); open('build/concat.txt','w').write(''.join(\"file '%s'\n\"%p for p in fs))"
ffmpeg -y -f concat -safe 0 -i build/concat.txt -c copy build/body.mp4

# 2. build the SFX track at the section/reveal timestamps, then mix and master
ffmpeg -y -i build/body.mp4 -i build/sfx_track.wav \
  -filter_complex "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a];\
[1:a]volume=1.0[s];[a][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -ac 2 -movflags +faststart \
  final/<name>.mp4
```

`-ac 2` matters: edge-tts is mono and YouTube plays a mono track noticeably
quieter and narrower. `+faststart` puts the moov atom first for streaming.

Persist the measured chapter start times (`sum of clip durations before each
section`) to `build/meta.json` — the description chapters must come from the
rendered clips, not from the script. Add 0.5-1.0 s to a section start so the
chapter does not fire while the previous sentence is still finishing.

## Step 9 — Thumbnail (question template)

- **Left side, two brush-stroke bands, tilted slightly:** line 1 white on
  black, line 2 black on yellow. Words with a digit or ₹ are highlighted
  automatically (yellow on black, green on yellow) — put the money and the
  count in digits. At most 4 words per line:
  - `kamai`: `<X> वाला | कितना कमाता है?`
  - `list`: `₹10,000 से शुरू | ये 7 बिज़नेस`
- **Green zig-zag growth arrow** top right on every thumbnail.
- **Art, right side:** the Boss large, hand on chin, curious and impressed, at
  the business, gold money (note stacks, a bowl of coins) in front, **left half
  empty**. Name the business + two props in English.
- **Optional green badge, bottom left:** one rupee figure the video states
  ("₹3,000/फेरा", "₹24,000/महीना"). Digits and ₹ only — **no Latin letters**.
- Mood: bright, curious, admiring — never alarmed. No red, no shock bait, never
  a real person's face.
- Check `thumbnail-210x118-preview.png`: both lines must read at phone size.
  Thumbnail says the same thing as the title.

## Step 10 — Title, description, tags (SEO from real queries)

### Before writing a word: pull the actual queries

Never invent the search phrase. Hit YouTube autocomplete for 10-15 seed terms:

```bash
curl -s "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=hi&gl=in&q=बिरयानी+बिजनेस"
```

Then read what comes back. Findings from the biryani episode (Oct 2026):
- `बिरयानी बिजनेस` surfaced *biryani business profit*, *biryani business kaise start kare*
- `biryani business` returned **"बिरयानी बिजनेस" as the #1 suggestion** — Hindi viewers type business queries in **Roman script**
- `biryani shop profit` had almost no Hindi results (only Tamil) — an open gap
- adjacent demand: `restaurant business hindi`, `ढाबा बिजनेस`, `खाने का बिजनेस`

So a Hindi business video needs **both scripts in the title**: the Devanagari
phrase first, the Roman keyword second. YouTube treats them as different
queries.

**Title templates** (40-90 chars):
- `kamai`: `<X> वाला कितना कमाता है? 💰 | <one specific, positive Hindi hook>`
- `list`: `₹<budget> से शुरू करें ये <N> बिज़नेस 🔥 | <one honest hook>`
- bilingual (preferred when a Roman query exists): `<Hindi keyword> में कितना प्रॉफिट? ₹<figure> महीना | <Roman keyword> का पूरा हिसाब`

The hook names a unit the viewer can picture (1 लीटर, एक फेरा, एक प्लेट, एक कप).
No "करोड़ों की कमाई", no promise the video does not keep. Put two variations in
`title_alternates` for Test & Compare.

**Description:**
```
[Myth hook in Hindi + main Hinglish search phrase, within the first 150 characters.]

[2-3 Hindi sentences on what the video reveals, respect for the owner, no RAAZ spoiler.]

⏱️ Chapters
0:00 [hook label]
0:xx रमेश की कहानी
0:xx पैसा कहाँ से आता है
0:xx मालिक की समझदारी
0:xx सबक

🔍 आपके सवाल (Your Queries):
[15-20 search phrases: Hinglish, Devanagari, English]

📚 Sources
- [source] — [URL]

🎩 Business Mafia — हर धंधे का असली हिसाब, हिंदी में।

#BusinessMafia #BusinessModel #[TopicHashtag]
```

At least four chapters, first at 0:00, taken from `timings.json`. A `list`
episode gets one chapter per idea.

**Tags:** 15-25, under 500 chars: main query in Hinglish + Devanagari + English
("chai wala kitna kamata hai", "चाय वाला कितना कमाता है", "chai business profit"),
cost/investment variants, misspellings, series terms ("business model in hindi",
"Business Mafia").

**Engagement package:** `pinned_comment` (bonus fact + question), `community_post`
(one-line poll), `shorts_hook` (`{start, end}` 30-55 s from `timings.json`).

## Step 11 — Upload to Business Mafia (Amplifier bridge)

The channel is already connected and authenticated in the Amplifier dashboard
(https://amplifier-sand.vercel.app) as **Business Mafia**
(`UCcm8EqvJwq9WfPdDJG06f1g`). Uploading is **per target channel**: only that
channel receives the video. Do not fan out to other connected channels.

Default target: **Business Mafia** (`--channel` / `AMPLIFIER_CHANNEL`).

The agent key lives at `~/.config/amplifier/agent_key` (or `AMPLIFIER_API_KEY`).
Do not print it.

```bash
cd <workdir>
SKILL_DIR=~/.claude/skills/business-mafia-yt-skill
python3 "$SKILL_DIR/scripts/upload_to_amplifier.py" \
  --video final/<name>.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Business Mafia" \
  --cleanup
# add --privacy public to publish immediately; default is private for review
# add --cleanup-keep-video to keep the master MP4 locally
```

`--cleanup` runs `cleanup_after_upload.py` automatically once the upload returns
a video id. See Step 12.

`final_upload_metadata.txt` contains `Title:`, `Description:`, `Tags:`
(comma-separated) and optionally `Privacy:`. Explicit flags such as `--title`,
`--description-file`, `--tags` override the file.

What it does:
1. Finds the channel by title via `GET /api/channels` (fails loudly if missing).
2. Mints a short-lived YouTube access token via `GET /api/channels/<id>/token`.
3. Streams the local file straight to YouTube (resumable upload, no Cloudinary
   size/memory ceiling).
4. Sets the custom thumbnail (warning only if YouTube rejects it).
5. Registers the upload with Amplifier (`POST /api/publications/register`) so
   analytics can track it.
6. Prints JSON: `youtubeVideoId`, `youtubeUrl`, `amplifierVideoId`, `privacy`.

Fallback (small videos only): add `--via-cloudinary` to stage on Cloudinary and
let the Amplifier server do the YouTube upload.

Before a real upload, validate the channel, key, and metadata with `--dry-run`
(mints a token but uploads nothing). Add `--analytics --wait 60` to print initial
stats in the same run.

## Step 12 — Post-upload cleanup (automatic)

Each episode leaves ~300 MB on disk: 85 frame plates, 85 clips, two audio sets,
SFX and a ~70 MB master. Ten episodes is 3 GB of things that already live on
YouTube.

After a **verified** upload, run:

```bash
python3 "$SKILL_DIR/scripts/cleanup_after_upload.py" \
  --workdir <workdir> --video-id <youtubeVideoId> --title "<title>" --yes
```

or just pass `--cleanup` to the upload script and it happens in the same run.

**Deleted:** `clips/`, `clips_ov/`, `images/`, `images2/`, `images3/`, `audio/`,
`audio2/`, `sfx/`, `tmp/`, `build/*.mp4`, `build/*.wav`, `build/concat.txt`,
`build/*.ass`, `build/*.srt`, and `final/*.mp4` (the master).

**Kept** (~200 KB, enough to re-open or re-upload later):
- `uploaded.json` — video id, URL, title, channel, privacy, upload time, bytes freed
- `final/thumbnail.jpg`, `final/script.md`, `final/metadata.md`
- `final/description.txt`, `final/title.txt`, `final/tags.txt`
- `build/*.py` — the generators, in case a beat needs re-cutting

Safety rails — do not remove them:
1. It **refuses to run without a video id**.
2. It **verifies the id on YouTube** via oEmbed before deleting; if the check
   fails it deletes nothing.
3. It writes `uploaded.json` **before** the first delete.
4. It refuses to run in a directory that does not look like an episode workdir.
5. `--dry-run` prints the plan and the byte count without touching anything.
   Run the dry run the first time you use it on a new machine.

Never clean after a failed or unverified upload. If the upload errored, stop and
ask — the master may be the only copy.

Then confirm:

```bash
du -sh <workdir>        # expect ~1 MB, not 300 MB
cat <workdir>/uploaded.json
```

## Step 13 — Analytics

After upload (views/likes need a little time to appear):

```bash
python3 ~/.claude/skills/business-mafia-yt-skill/scripts/amplifier_analytics.py \
  --channel "Business Mafia" --range 28d
```

- Per-video: `--video <amplifierVideoId>` (from Step 11 output).
- Whole account: `--overview`.
- Force a fresh pull from YouTube first: add `--refresh` (throttled to 15 min
  per video by the API).

Report totals (views, likes, comments, watch minutes, subs gained) and the
per-video breakdown, not just raw JSON.

## Output files

Before cleanup:
- `final/<name>.mp4` — 1080p, 8-12 min (480-720 s), -14 LUFS, stereo
- `final/thumbnail.jpg` — 1280x720 with the two-band Devanagari title
- `final_upload_metadata.txt` — title, description, chapters, tags

After cleanup (the durable set):
- `uploaded.json` — video id, URL, title, channel, privacy, upload time, bytes freed
- `final/thumbnail.jpg`
- `final/script.md`, `final/metadata.md`
- `final/description.txt`, `final/title.txt`, `final/tags.txt`
- `build/*.py` — the generators

## Bundled scripts
- `scripts/gen_images.py` — Perchance bulk image generator (edit `SUBJECTS`); three style presets (`STYLE_PRESET=boss|xiaohei|qhuman`) and two compositions (`COMPOSITION=single|islands`). Landscape 768x512, verifies the prompt took, retries 3x.
- `scripts/trim_silence.py` — removes edge-tts dead air and remaps the SRT through the cuts.
- `scripts/build_ass.py` — SRT → animated Devanagari ASS (3-word chunks, edit `KEYS`/`MONEY`).
- `scripts/prep_frames.py` — 3:2 renders → full-bleed 1920x1080 plates (no pad seam).
- `scripts/make_sfx.py` — synthesizes whoosh/ding/sting, no sample files needed.
- `scripts/mix_sfx.py` — iterative whoosh mixer (legacy; `make_sfx.py` + the Step 8 mix is preferred).
- `scripts/upload_to_amplifier.py` — upload to **Business Mafia** + register for analytics; `--cleanup` reclaims disk after success.
- `scripts/cleanup_after_upload.py` — verified post-upload asset deletion.
- `scripts/amplifier_analytics.py` — channel/video/overview analytics.

## Quality gate

1. Runtime 480-720 s **(measure it, don't estimate)**; audio -14 LUFS; **zero
   silences longer than 0.45 s** — run the `silencedetect` check from Step 2.
2. Every scene: Boss on-model (black fedora + gold band, no mouth), palette
   black/white/gold (`qhuman` may add natural skin tone only), no shading, no
   on-image text, at most two characters. Reroll bad beats.
3. Scenes 7-10 s each, one per beat, **18-22 Hindi words per beat**. Frames are
   full-bleed 1920x1080, no white pad seam.
4. Every rupee figure, date and "first" claim is sourced or said as an estimate.
5. First sentence: a rupee shock or a question. The `[RAAZ]` secret is teased in
   `[HOOK]` and paid off.
6. Thumbnail: Boss on-model, large on the right, left half clear, two-band title
   reads at 210x118, green arrow present, title and thumbnail ask the same question.
7. Captions legible (74/outline 6); conjuncts, nukta and i-matra correct;
   ambience never masks the voice.
8. Metadata complete: title, description with chapters/queries/sources, 15-25 tags.
9. **Post-upload:** video verified live (oEmbed + maxres thumbnail), `uploaded.json`
   written, then local assets cleaned. `du -sh` on the workdir should be ~1 MB.

## When to stop and ask the human

- A topic would name a living person in a critical light, accuse a named company
  of wrongdoing without a court or regulator finding, or touch caste or religion
  beyond a respectful documented overview.
- Sources conflict on a central figure and you cannot resolve it.
- A brand change is implied (voice, art, palette, format).
- A credential appears in a chat message, or anything would cost money, need
  terms signed, or post anywhere beyond the authorized Business Mafia channel.

## Notes
- Visual language adapted from [hi-nikola/hand-drawn-explainer-video-nikola](https://github.com/hi-nikola/hand-drawn-explainer-video-nikola) (Apache-2.0); its Xiaohei preset credits [ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations). Keep this attribution if the skill is shared or republished.
- One preset per video. Do not mix `boss`, `xiaohei` and `qhuman` inside one episode.
- Never use background music (channel preference).
- Upload goes to **one** channel only: **Business Mafia** (`--channel` target).
- Default privacy is `private`. Pass `--privacy public` only when the user asked
  for the video to go live immediately.
- Never print or commit the agent key.
- Hindi length is earned with more substance, never padding.

## Lessons from the biryani episode (2026-10-20)

First full run of this skill. What broke, and what is now baked in above:

- **Runtime miss:** 85 beats × ~11 words = 926 words → 6:35, not the 8-12 min the
  beat count implied. Word budget table added to Step 1.
- **"Annoying pauses":** edge-tts silence was 30% of the runtime. `trim_silence.py`
  exists because of this; run it before captions, never after.
- **Devangari captions:** `shaping=complex` does not exist in ffmpeg 6.1 — it
  errors. Default libass shaping was correct all along.
- **Pad seam:** scaling 768x512 to 1080p and padding leaves a visible card around
  every drawing. `prep_frames.py` cover-crops instead.
- **Perchance:** setting the style select to "No style" (unicode text) silently
  breaks generation; leave it alone. Always verify the prompt textarea took the
  text, or you get a random image.
- **SEO:** Hindi business searches are typed in Roman script about half the time.
  Title carries both scripts.
- **Disk:** ~300 MB per episode. `cleanup_after_upload.py` (or `--cleanup`) runs
  only after the video id verifies on YouTube.
