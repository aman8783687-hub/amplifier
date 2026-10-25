# Format B — the dark cinematic explainer ("Do It Anyway" look)

This is the second production format for RedHat Engineer, proven on
`episodes/2026-10-23-do-it-anyway` (https://youtu.be/aAAGPQTVxsA, 14:04, 105 scenes).
It exists because the operator asked for a video in the visual language of a
high-performing reference channel, not the whiteboard "How X Was Built" house style.

**Format A ("How X Was Built") stays the default.** Use Format B only when the
operator asks for a psychology / self-improvement / long-form cinematic episode,
or explicitly asks for "the Do It Anyway style". Everything below is the locked
recipe — follow the numbers, don't re-derive them.

## The look (locked values)

| Element | Value |
|---|---|
| Background | Solid black `#050506` in the frame, **pure black `#000000` inside the generated art** |
| Line / body colour | Cream white `#F7EFE0` |
| Accent | Red `#E5332A` — one accent per frame, never a second |
| Character | Stick figure, **one oversized round cream head**, two black oval eyes, no mouth, no nose, thin cream limbs, small red scarf |
| Line quality | Hand-drawn brush-pen, slightly rough edges, flat 2D |
| Depth | Flat. No gradients in the art, no shading, no 3D, no glow bloom beyond one soft red highlight |
| Space | Lots of empty black. The frame should feel under-filled, not busy |
| Text in art | **None.** All words are added by the renderer, never baked by the image model |

The style suffix passed to the image model, verbatim (also in
`channel_state.json` → `format_cinematic.style_suffix`):

> Minimalist hand-drawn ink cartoon on a pure solid black background. The character is a stick figure with one oversized round cream-white head, two black oval eyes, no mouth, no nose, thin cream-white stick limbs, loose confident brush-pen strokes, slightly rough hand-drawn outlines. Flat 2D, high contrast, lots of empty black space, only cream-white, black and one red accent. No text, no letters, no numbers, no logos, no gradients, no shading, no 3D.

Character consistency comes from **one** reference image, reused forever:
`brand/cinematic-character-ref.png`. Never regenerate it per episode; every scene
is conditioned on it. If it is ever replaced, that is a logged brand change.

## Runtime and shape

- **10–16 minutes.** The 2026-10-23 episode ran 14:04. Do not force this into the
  5–7 minute Format A gate; the length is part of the appeal (it reads as a
  "full breakdown", which is what earns the long watch time).
- **~165 words per minute** of narration. 2,300 words ≈ 14 minutes; 2,450–2,650 ≈ 15–16.
- **6 chapters**, each announced by a kicker card in the top-left corner. A chapter
  is 1.5–4 minutes long. Six is the ceiling — more and the labels become noise.
- Open cold on the specific, concrete moment (an alarm going off), not on a thesis.
- Close on permission, not a summary: tell the viewer they were not broken, then
  one direct question that invites a comment.

### Chapter structure that worked

| Chapter | Job | Length |
|---|---|---|
| THE MIND | State the paradox + the counter-intuitive study that proves it | ~2:15 |
| LEARNED INDUSTRIOUSNESS | The mechanism: effort is a sensation that can be rewarded | ~1:30 |
| THE DOPAMINE LIE | The neuroscience: reward prediction error, why starting feels bad | ~1:20 |
| WHERE IT WAS WRITTEN | The origin story: how childhood trained the prediction | ~2:30 |
| THE FIVE WAYS | The payoff. Five numbered tactics, one scene each | ~4:20 |
| WHAT ACTUALLY CHANGES | Honest limits, the 66-day figure, the closing line | ~2:00 |

The five tactics chapter is the retention engine: number them out loud
("One… Two…") so the viewer knows how much is left and stays for the last one.

## Script format

Identical beat syntax to Format A so the tooling works unchanged:

```markdown
# Title
Series: The Mind | Target runtime: 14:40

[HOOK]
1. There are about forty seconds every morning that quietly decide your entire day.
2. Your alarm goes off. Your eyes open in the dark.
...
[SETUP]
31. To understand the trick, you need one strange idea from psychology.
...
[ESCALATION]
...
[TURN]
...
[LANDING]
```

Rules that matter more here than in Format A:

- **One sentence per beat.** 8–18 words. Format B lives on short declaratives
  stacked into a rhythm; long compound sentences kill the cadence.
- **Every claim carries a name, year and finding** in the script or in
  `01_research/sources.md`. This format attracts "source?" comments — be ready.
- Sections still drive the voice presets (`hook` / `setup` / `escalation` /
  `turn` / `landing`), so keep the five headers even though chapters differ.
- Write the beats so a scene can be drawn from each: concrete nouns, visible
  actions, one idea per beat. "It predicts strain and self-criticism" is a scene;
  "discipline is complex" is not.

## Scene plan — `05_scenes/scenes.json`

105 scenes for 14 minutes ≈ 8 seconds each. Schema:

```json
{ "id": 7, "beats": [11, 12],
  "prompt": "the character writing a fresh neat plan on a sheet of paper at his desk, a tidy stack of papers beside him",
  "motion": "in", "kicker": "THE MIND",
  "overlay": {"text": "DAY 1"} }
```

- `beats` — which script beats this scene covers. **1–2 beats.** Consecutive,
  non-overlapping, and every beat 1..N must appear exactly once.
- `prompt` — the visual, written as a shot description. No style words (the suffix
  adds those), no text, no artist names. Include camera grammar where it helps:
  "close view of", "wide", "seen from behind".
- `motion` — `"in"` (push in: emphasis, close-up, reveal) or `"out"` (pull out:
  establishing, scale, aftermath). Alternate deliberately; never leave it default.
- `kicker` — chapter title, set only on the first scene of a chapter.
- `overlay` — a 2–4 word full-width text card (max ~3 s). Use 6–10 per video,
  always on a beat that states a number, a label or a verdict ("DAY 3",
  "EFFORT = REWARD", "A PREDICTION PROBLEM"). Overlays hide captions while shown,
  so never put one under a sentence the viewer must read along with.

Shot rhythm: establish → close → wide → object detail → reaction. A 14-minute
video with 105 scenes can afford 3–4 consecutive dialogue-free visual beats.

**Never** ask the image model to draw 3+ distinct characters (it collapses them).
Write group beats as shot/reverse-shot pairs, or as a crowd of featureless figures.

## Captions

Same grammar as Format A, different implementation (Remotion, see
`remotion-render.md`):

- Anton, uppercase, white with a heavy black stroke (`5px`) and soft shadow.
- 3 words per phrase, split early on any pause > 0.30 s.
- The spoken word turns red and lifts 3 px. Nothing else moves.
- Bottom-centred, 78 px from the bottom, max width 1560 px, 62 px type.
- Hidden while an overlay card is on screen.

## Audio

- Voice: edge-tts `en-US-AndrewMultilingualNeural`, chunked 1–3 sentences, exactly
  as `voice-and-audio.md` describes. Chunk plan still groups ≤52 words / ≤3 beats.
- Mastered to −14 LUFS, true peak ≤ −1 dBTP.
- **Voice only.** No music. No sound-effects bed for this format — the silence
  between beats is doing the work, and a whoosh every 8 seconds fights the pacing.

## Packaging and SEO

This format is search-led, not browse-led. The reference video earned 3.7M views
on an exact-phrase title; copy that logic, not its wording.

- **Title:** `The Psychology of [X] (Why You [Specific Failure])` — 45–55 chars.
  First clause = the exact phrase people type. Parenthetical = the curiosity gap.
  Example shipped: `The Psychology of Discipline (Why You Quit at 6AM)`.
- **Thumbnail:** one giant head or object, one 2–4 word phrase, one red accent,
  readable at 210×118. Operator-supplied thumbnails are used **as delivered** —
  do not regenerate them.
- **Description:** open with a 2-sentence hook, then a paragraph naming every
  researcher and finding, then the five tactics as prose, then a personal closing
  line, then chapters, then a linked source list, then the synthetic-media
  disclosure and a not-medical-advice disclaimer.
- **Tags:** cap at **444 characters including YouTube's quotes** (the API rejects
  anything over 500 with `invalidTags`). ~19 tags: exact phrase, variants,
  researcher names, adjacent topics, channel name.
- **Hashtags:** 3, above the fold in the description.

## Quality gate — Format B

Run in addition to the general gate in `SKILL.md`:

1. Every script beat is covered by exactly one scene; no gaps, no overlaps.
2. No scene runs longer than 12 s; average 7–9 s.
3. Character on-model in every frame he appears: one oversized cream head, two
   dot eyes, no mouth, red scarf only.
4. No text baked into any generated image (check the 10 busiest scenes).
5. Overlays: ≤10 total, ≤4 words each, never over a sentence the viewer is reading.
6. Captions spot-checked on the ten hardest names (Hofmann, Baumeister, Inzlicht,
   Eisenberger, Milkman, Schultz…), and they never collide with an overlay.
7. Chapters start within 1 s of the first beat that introduces them.
8. Render is 1920×1080, 24 fps, has audio, −14 LUFS ±0.5, true peak ≤ −1 dBTP.
9. `07_edit/captions.srt` exists and matches the spoken words.
10. Thumbnail is 1280×720 and legible at 210×118.

## Failure modes seen in production

- **Cloudflare free quota (10,000 neurons/day) runs out mid-batch.** 105 scenes at
  1024×576 will exhaust it. Generate reference first, then batch; when you hit
  429, keep the first-pass art for the remaining beats and log the debt rather than
  blocking the episode.
- **Cream-on-black drifts grey.** If a scene comes back with a grey field, the
  model ignored "pure solid black" — reroll with `--beats N --seed <new>`.
- **The character gains a mouth.** Reroll. A mouth completely changes the read of
  the face and breaks the style lock across the video.
- **Too much detail in the prompt** produces busy frames. This style is strongest
  when the prompt is one action, one object, one location.
