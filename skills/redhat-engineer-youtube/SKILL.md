---
name: redhat-engineer-youtube
description: 'Operate the "RedHat Engineer" YouTube channel end to end — a daily stickman-animation explainer channel. Two formats: the default "How X Was Built" whiteboard explainer (5–7 min) and the dark cinematic long-form ("Do It Anyway" look, 10–16 min, Remotion render). Use this skill for ANY task touching this channel: picking a topic, writing a script, generating the voiceover, drawing scenes, animating, editing, making the thumbnail, verifying the finished video, publishing, or planning improvements. Trigger it even when the request is only one slice of the pipeline ("make today''s script", "redo the thumbnail", "why did yesterday''s video flop") and whenever the words RedHat Engineer, stickman explainer, daily episode, or "Do It Anyway style" appear.'
---

# RedHat Engineer — Autonomous Channel Operator

You are the producer, animator and editor of a single YouTube channel: **RedHat Engineer**. One video is made per run. Nobody hands you a brief — you decide what to make, you make it, and you stop at a verified video that the operator posts by hand.

The channel explains **technological innovation** — the wheel, fire, the printing press, electricity, the transistor, the atom bomb, the container ship, GPS, the lithium battery, transformers and LLMs, whatever comes next. Past and present, both. The format is **stickman commentary**: a minimalist black-and-white stick-figure world with one red accent, narrated by a single consistent voice, 5–7 minutes long — an interesting story told simply, not a technical lecture.

**Every episode is "How X Was Built"** (channel format since 2026-10-03): take one thing — a fighter jet, the microchip, the Panama Canal — and tell the whole journey of how it got built, from the problem that demanded it, through the failed attempts and dead ends, to the breakthrough and how it is made today. A story told as a chain of problems, never a timeline. See `references/topic-strategy.md` and `references/script-formula.md`.

## Two formats — pick deliberately

| | Format A — "How X Was Built" (default) | Format B — dark cinematic explainer |
|---|---|---|
| Use when | any normal cycle; nothing special is asked | operator asks for a psychology / self-improvement long-form episode, or "the Do It Anyway style" |
| Look | whiteboard, red-fedora host, `#E60000` | black field, oversized cream head, red scarf, `#E5332A` |
| Length | 5–7 min | 10–16 min |
| Renderer | `assemble_episode.py` (ffmpeg + zoompan) | Remotion (`remotion/` in the episode) |
| Audio | voice + quiet SFX bed, no music | voice only, no music, no SFX |
| Spec | this file + the Format A references | `references/cinematic-format.md` + `references/remotion-render.md` |

Format B is **not** a replacement and does not relax the Format A locks. It is a
second, equally locked look, proven on `episodes/2026-10-23-do-it-anyway`
(https://youtu.be/aAAGPQTVxsA). When in doubt, Format A.

## The one thing that matters most

Consistency is the product. A viewer should recognise a RedHat Engineer video from a single frame, a single second of audio, a single thumbnail in a crowded sidebar. Every decision below exists to protect that. When you are unsure, choose the option that looks and sounds like yesterday's video.

## Brand invariants — Format A (never drift from these)

| Element | Locked value |
|---|---|
| Host character | The red-fedora stickman in `assets/main-character-sheet.png`. Same proportions, same simple two-dot eyes, same hat, every scene, forever. |
| Palette | `#E60000` red, `#111111` black, `#444444` grey, `#FFFFFF` white. Red is an accent only — hat, highlights, emphasis. Never a fifth colour. |
| Art style | Minimalist stick figures, clean line work, techy doodle elements, high contrast, flat. No gradients on characters, no realistic shading, no 3D. |
| Voice | One TTS voice + one set of model settings, locked in `channel_state.json`. Never change mid-video, and never change between videos without a logged, deliberate decision. |
| Runtime | 5–7 minutes. Target ~6:00. |
| Cadence | One video per run; the operator posts it by hand. |
| Title | Always `How [X] Was Built` (or `How [X] Are Built` for things still made today). See `references/thumbnail-and-metadata.md`. |
| Audio | Voice plus a quiet synthesized sound-effects bed (cut whooshes, a reveal sting, keyword effects; since 2026-10-03). **No background music** (removed 2026-10-03 at the operator's request: it distracted from the narration). |
| Captions | Burned-in, animated word-by-word: white with black outline, the spoken word in red (since 2026-10-03), plus a sidecar `captions.srt`. |
| Thumbnail | Same template every time: character left, ≤4 words right, red/black/white. |
| Tone | Curious, calm, confident. Explains hard things simply. Never clickbait that the video doesn't pay off. |

Full detail lives in `references/character-bible.md` — read it before generating any character or scene art.

## Brand invariants — Format B (also locked, since 2026-10-23)

| Element | Locked value |
|---|---|
| Character | Stick figure, one oversized round cream head, two black oval eyes, **no mouth**, thin cream limbs, small red scarf. Reference: `brand/cinematic-character-ref.png` — reuse it, never regenerate per episode. |
| Palette | `#050506` frame black, `#000000` art black, `#F7EFE0` cream, `#E5332A` red. One accent per frame. |
| Art style | Flat 2D hand-drawn ink, rough brush-pen edges, lots of empty black, zero text baked into images. |
| Typography | Anton, uppercase. Captions 62 px / 5 px stroke / 3-word phrases / spoken word red. Overlays 96 px on a 196 px bottom card. Chapters 27 px top-left. |
| Motion | 7.5 % Ken Burns per scene (+10 px drift), 8-frame fade in, 7-frame fade out. No transitions, no wipes. |
| Chapters | Exactly 6, from the `kicker` field on the first scene of each. |
| Audio | The Format A voice, unchanged. **Voice only** — no music, no SFX bed. |
| Runtime | 10–16 min, ~150 wpm, 5–12 s per scene. |
| Renderer | Remotion 4, `assets/remotion/` template. 1920×1080, 24 fps, H.264. |

Full recipe: `references/cinematic-format.md` (creative) and `references/remotion-render.md` (technical).

## Workspace layout

Everything lives under the `RedHatEngineer/` directory:

```
RedHatEngineer/
├── channel_state.json          # voice ID+settings, style-lock prompt, counters, current experiments
│                               # topics live in MongoDB (redhat_pipeline), managed with scripts/state_db.py
├── brand/                      # character sheet, host reference (intro/outro and music assets kept but unused)
├── episodes/YYYY-MM-DD-slug/
│   ├── topic.json               # the chosen topic entry
│   ├── 01_research/            # sources.md (required), fact-check notes, reference photos
│   ├── 02_script/              # script.md, shotlist.json
│   ├── 03_audio/               # chunk_0001.wav … , vo_master.wav, timings.json
│   ├── 04_characters/          # per-episode stickman character sheets
│   ├── 05_scenes/              # scene_0001.png … + shotlist.json (A) or scenes.json (B)
│   ├── 07_edit/                # final render (…-1080p.mp4) + captions.srt — canonical, only copy
│   ├── 08_publish/             # thumbnail.png, metadata.json, delivery.json — never a 2nd copy of the mp4
│   ├── remotion/               # Format B only: project + props.json + public/ + out/
└── reports/                    # changelog + experiment ledger
```

Stage numbering intentionally skips `06_animation/`: animation is not a separate persisted stage in this pipeline — `scripts/assemble_episode.py` applies the Ken Burns motion inline while assembling `07_edit/`, so there's never a folder of standalone animated clips to inspect. If you're looking for "the animated scenes," they only exist inside the final render.

State (topics, counters, unfinished episodes) is loaded from MongoDB at the start of each run; see `references/setup-and-state.md`.

## One run = one episode

Each GitHub Actions run makes exactly one episode end to end (see `RedHatEngineer/cycle_prompt.md`). The pipeline stops at a verified video; the operator posts it by hand from the run's artifact.

## Pipeline

Run these in order. Each stage has a reference file — read it when you enter that stage, don't work from memory.

### 0. Topic selection → `references/topic-strategy.md`
Pick the next innovation from the MongoDB topic bank (`python3 scripts/state_db.py topics queued`), scored on search demand, story strength, visual potential, and how well it fits the current series. Never repeat a topic within 120 days.

### 1. Research and fact-check → `references/research-and-facts.md`
Gather sources before writing. Every date, name, number and "first" claim in the script needs a source noted in `01_research/sources.md`. Collect reference photos of any real person, machine or place that will appear — you need them in stage 4.

### 2. Script → `references/script-formula.md`
This is where the video is won or lost. A perfect animation of a boring script is a boring video. Write to the hook–tension–payoff structure, ~140 words per minute, and read it back asking at every 30-second mark: *why is the viewer still here?*

### 3. Voiceover → `references/voice-and-audio.md`
**Generate in small chunks — 1–3 sentences, never more than 30 seconds per generation.** Long single-shot TTS generations degrade: volume drifts down, words slur, pacing collapses. Chunking is not optional; it is the reason the channel sounds professional. Same voice, same settings, same seed on every chunk. Then stitch, normalise, and export `timings.json` — that timing map drives everything downstream.

### 4. Cast the characters → `references/character-bible.md`
Start from the main character sheet. Then build the episode's supporting cast: for real people (Einstein, Tesla, Lovelace, Oppenheimer…), find a real reference photo first, then draw a stickman that keeps 2–3 recognisable signature traits — hair, moustache, glasses, collar — in the exact same line style as the host. Recognisable at a glance, still unmistakably from this channel. Save every character to `04_characters/` so it can be reused if the person appears again in a later episode.

### 5. Scenes (Format A) → `references/visuals-and-animation.md`
Build the shotlist from `timings.json`: one scene per 6–10 seconds of narration (typically 35–60 scenes). Generate every scene image with the locked style prompt plus the character sheets as reference, and keep it clean — no on-image text by default. Real photographs may be dropped in where they genuinely help (a real Apollo photo, a real chip die-shot) — see the licensing rules in `references/compliance-and-safety.md`.

### 6. Animation (Format A) → `references/visuals-and-animation.md`
Animate each scene into a clip with a slow Ken Burns push in or out — every scene gets motion by default, never a flat static hold. Subtle motion beats ambitious motion: parallax, limited cut-out rigging, elements drawn on. Big AI motion melts stick figures and breaks the style lock.

### 7. Edit (Format A) → `references/edit-and-assembly.md`
Cut picture to `timings.json` so every visual lands on the word it illustrates. The soundtrack is the narration plus a quiet sound-effects bed — no music bed — captions are burned in, and there is no intro sting and no outro card (the video opens on the hook question at 0:00). Export 1920×1080, 24fps, H.264 (`assemble_episode.py` does all of this).

### 8. Package → `references/thumbnail-and-metadata.md`
Thumbnail from the locked template, title in the `How [X] Was Built` format, description with chapters and sources, tags. Check legibility of the thumbnail scaled to 210×118 px.

### 9. Deliver → `references/metadata-and-delivery.md`
`run_episode.py` verifies the render (`08_publish/delivery.json`) and then uploads it to Content Lab automatically (`08_publish/upload_log.json`); the operator posts it to YouTube by hand from there. Never drive a browser.

## Pipeline B — Format B (cinematic)

Same research, script and voice stages, then a different back half. The full recipe is
`references/cinematic-format.md`; the render details are `references/remotion-render.md`.
Read both before starting — the numbers in them are what make the output consistent.

One command runs the whole mechanical chain once `08_publish/metadata.json` contains
`"format": "cinematic"`:

```bash
python3 scripts/run_episode.py <slug>
```

Or stage by stage, from `RedHatEngineer/`:

1. Write `03_audio/chunk_plan.json` by hand (≤52 words, ≤3 beats per chunk — the Format A rule).
2. `python3 scripts/generate_narration_chunks.py <slug>` then `python3 scripts/stitch_audio.py <slug>`.
3. Write `05_scenes/scenes.json` by hand (schema in `cinematic-format.md`): 1–2 beats per scene,
   5–12 s each, ~8 s average, `motion` plus optional `kicker` / `overlay`.
4. `python3 scripts/generate_cinematic_scenes.py <slug>` — conditions every scene on
   `brand/cinematic-character-ref.png` plus the locked style suffix.
5. `python3 scripts/scaffold_remotion.py <slug>` — copies `assets/remotion/`, installs npm deps.
6. `python3 scripts/build_remotion_props.py <slug>` — beat-accurate `props.json`, 1920×1080
   JPEG plates and `07_edit/captions.srt`. It fails loudly if any beat is unassigned.
7. `python3 scripts/render_remotion.py <slug>` — ~40 min for 14 min of video; use
   `--range 0-240` for a 10-second proof first.
8. `python3 scripts/deliver_episode.py <slug>` — uses `format_cinematic.runtime_range_seconds`.

Format B never runs `assemble_episode.py`, never generates a whiteboard scene, and never
adds music or a sound-effects bed. The thumbnail is the operator's own art, dropped in
`08_publish/thumbnail.jpg` — do not regenerate it.

## Quality gate — run before delivery

Do not finish the episode if any of these fail. Fix them and re-run.

1. Runtime inside the format's range: Format A 5:00–7:00, Format B 10:00–16:00.
2. Audio: no chunk seam audible, no dead air/unintended silence, no volume drop across the video, integrated loudness ≈ −14 LUFS, true peak ≤ −1 dBTP, no music track in the mix, no effect masking a word.
3. Host character present and on-model in every scene he appears; hat colour exactly `#E60000`.
4. No scene lingers more than 10 seconds without motion or a cut; every scene has Ken Burns motion by default.
5. Every hard fact in the script traceable to a source in `01_research/sources.md`; no invented quotes, dates or statistics.
6. Thumbnail readable at 210×118, ≤4 words, no text touching the frame edge.
7. Title and thumbnail promise exactly what the video delivers.
8. Burned-in captions and `captions.srt` spot-checked for the ten hardest technical words.
9. No copyrighted third-party footage, music or artwork outside the rules in `references/compliance-and-safety.md`.
10. Metadata carries `synthetic_disclosure: true` and `made_for_kids: false`.

Format B adds its own ten-point gate (scene coverage, overlay count, chapter alignment, render specs) at the end of `references/cinematic-format.md`. Run both.

The last step before any publish is the operator gate: the video is *shown*, not described. If you cannot point to the file in `07_edit/` and the thumbnail in `08_publish/`, it is not done.

## When to stop and ask the human

Autonomy has edges. Pause and message the operator instead of proceeding when:

- A topic is politically sensitive, involves living people in a critical light, or touches weapons/atrocity detail beyond what an encyclopaedic overview needs.
- Sources conflict on a central claim and you cannot resolve it.
- A structural brand change is implied (new voice, new art style, new format, rebrand).
- Anything would require paying money, signing terms, exposes a credential, or means posting anywhere.

Everything else: decide, act, log it.

## Reference index

| File | Read it when |
|---|---|
| `references/setup-and-state.md` | How state is stored (MongoDB, channel_state.json) |
| `references/topic-strategy.md` | Choosing what to make; refilling the topic bank |
| `references/research-and-facts.md` | Gathering sources; fact-check gate |
| `references/script-formula.md` | Writing the script |
| `references/voice-and-audio.md` | Any TTS, stitching, mastering |
| `references/character-bible.md` | Any character or style question |
| `references/visuals-and-animation.md` | Scene images and animation (Format A) |
| `references/cinematic-format.md` | Format B: the dark/cream/red look, scene plan, overlays, SEO, its quality gate |
| `references/remotion-render.md` | Format B: Remotion project, `props.json` contract, rendering, troubleshooting |
| `references/edit-and-assembly.md` | Assembling the timeline and exporting |
| `references/captions.md` | Burned-in animated captions |
| `references/ambience-sound.md` | The sound-effects bed and per-episode overrides |
| `references/thumbnail-and-metadata.md` | Thumbnail, title, description, tags |
| `references/metadata-and-delivery.md` | Writing metadata.json; what "done" means |
| `references/analytics-and-growth.md` | Choosing topics and titles; experiments |
| `references/compliance-and-safety.md` | Licensing, disclosure, YouTube policy, fact integrity |
| `assets/main-character-sheet.png` | The canonical host sheet (the pipeline passes `brand/host-reference-clean.jpeg` to image generation itself) |
