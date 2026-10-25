# Remotion rendering (Format B)

`scripts/assemble_episode.py` (ffmpeg + zoompan) cannot do per-word caption timing,
chapter cards and text overlays without an ever-growing filtergraph. Format B renders
through **Remotion 4** instead: a React composition reads one `props.json` and writes
the MP4. The finished file is byte-for-byte equivalent in spec to Format A
(1920×1080, 24 fps, H.264, AAC) and lands in the same place, so delivery, packaging
and publishing are unchanged.

## What you need on the machine

- Node 18+ and npm (Remotion 4.0.538 is what was tested).
- A Chromium download on first render (`npx remotion browser ensure` if it complains).
- ~1.5 GB free disk per episode: `node_modules` ~500 MB, `public/` ~260 MB
  (images + a 232 MB WAV copy), plus the render.

## The pipeline, in order

All commands run from `RedHatEngineer/` with the episode slug:

```bash
python3 scripts/generate_narration_chunks.py <slug>   # unchanged from Format A
python3 scripts/stitch_audio.py <slug>                # writes vo_master.wav + timings.json + word_timings.json
python3 scripts/generate_cinematic_scenes.py <slug>   # 05_scenes/scene_XXX.png from 05_scenes/scenes.json
python3 scripts/scaffold_remotion.py <slug>           # copies the template, npm install
python3 scripts/build_remotion_props.py <slug>        # props.json + public/ + captions.srt
python3 scripts/render_remotion.py <slug>             # out/episode.mp4 -> 07_edit/…-1080p.mp4
python3 scripts/deliver_episode.py <slug>             # verification (reads format_cinematic range)
```

`scripts/run_episode.py <slug>` runs all of that unattended when
`08_publish/metadata.json` contains `"format": "cinematic"`.

## The template

Lives in the skill at `assets/remotion/` and is copied into
`episodes/<slug>/remotion/` by `scaffold_remotion.py`:

```
remotion/
├── package.json          remotion 4.0.538, @remotion/cli, @remotion/renderer,
│                         react 18, @fontsource/anton, @fontsource/inter
├── tsconfig.json
├── remotion.config.ts    h264 / crf 21 / yuv420p / jpeg 92 / concurrency 4 / swangle
├── src/index.ts          registerRoot
├── src/Root.tsx          <Composition id="Episode">, duration read from props
├── src/Video.tsx         scenes, Ken Burns, captions, overlays, chapters, progress bar
├── props.json            the whole video as data (built, never hand-written)
└── public/
    ├── scenes/scene_001.jpg …   pre-upscaled to 1920×1080
    └── audio/vo_master.wav
```

### `Video.tsx` — what it draws

| Layer | Behaviour |
|---|---|
| Scene | Each scene is a `<Sequence>` with a 7.5 % Ken Burns move (`in` or `out`) plus 10 px of drift, 8-frame fade in and 7-frame fade out, over `#050506` |
| Captions | 3-word phrases from `word_timings.json`; spoken word `#E5332A`, rest white, 5 px black stroke, 62 px Anton, hidden during overlays |
| Overlay | Full-width bottom card, 196 px tall, 3 px red top rule, 96 px Anton, last word red, 74 frames ≈ 3.1 s |
| Chapter | Top-left red dot + 27 px Anton, fades in/out over 14 frames, persists for the chapter |
| Progress | 5 px red bar on the bottom edge |

`Episode` composition is 1920×1080, fps from props (24). All typography is loaded
from `@fontsource`, so rendering never depends on system fonts.

## `props.json` contract

`build_remotion_props.py` produces this; nothing else should write it.

```json
{
  "fps": 24,
  "durationInFrames": 20258,
  "scenes": [
    { "from": 0, "to": 112, "image": "scenes/scene_001.jpg",
      "motion": "in", "overlay": null }
  ],
  "chapters": [
    { "text": "THE MIND", "from": 0, "to": 3241 }
  ],
  "phrases": [
    { "start": 0.0, "end": 1.24,
      "words": [{"text": "There", "start": 0.0, "end": 0.18}] }
  ]
}
```

- `scenes[].to` is **set from the next scene's `from`**, so rounding can never leave
  a one-frame gap; the last scene runs to `durationInFrames`.
- `image` paths are relative to `public/` and are `staticFile()`-resolved.
- `chapters` come from the first scene carrying each `kicker`; a chapter ends where
  the next kicker starts.

### How beat timing is derived

`timings.json` gives chunk start/end; `word_timings.json` gives every word's absolute
time. For each chunk, the first beat starts at the chunk start; each following beat is
located by fuzzy-matching its first three words against the chunk's word list
(`SequenceMatcher`, threshold 0.55). Fallback is proportional interpolation.
`build_remotion_props.py` prints any beat it could not place — **zero missing beats is
a hard requirement**, otherwise scenes silently collapse to 0-length.

## Rendering

`render_remotion.py` wraps:

```bash
npx remotion render src/index.ts Episode out/episode.mp4 \
  --props=props.json --concurrency=4 --log=info
```

- **Performance:** ~7–8 fps at 1080p on a 4-core CPU, so a 20,258-frame episode takes
  ~40 minutes. This is CPU-bound; concurrency 4 is right for 4 cores.
- **The single biggest speed win:** pre-upscale every scene to 1920×1080 **JPEG**
  in `public/` (Lanczos, quality 95) instead of letting Remotion decode 1024×576 PNGs.
  Same for keeping `props.json` small — it is data, not frames.
- `swangle` in `remotion.config.ts` is required on headless Linux without a GPU. If
  Chromium crashes with a GL error, that setting is the first thing to check.
- Use `--range 0-240` on `render_remotion.py` for a 10-second proof before committing to a
  full render. The wrapper translates it to Remotion's own `--frames` flag; passing `--range`
  straight to `npx remotion render` is silently ignored and kicks off the entire video.

### Disk notes

`public/audio/vo_master.wav` is a 232 MB copy of the real master; the render only
needs it as a source file. Do not delete the original in `03_audio/`. After a
successful delivery and upload, `remotion/public/` and `remotion/node_modules/` are
safe to delete to reclaim ~800 MB — keep `src/`, `props.json` and `package.json` so
the episode can be re-rendered.

## QC frames

```bash
ffmpeg -ss 00:02:14 -i 07_edit/redhat-engineer-<slug>-1080p.mp4 -frames:v 1 /tmp/qc1.png
```

Grab one frame per chapter at minimum, plus every overlay, to check captions and
overlay collisions. Compare a frame against `05_scenes/scene_XXX.png` to confirm the
Ken Burns transform never crops the character's head.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot find module '@remotion/...'` | `node_modules` missing after a fresh clone | `python3 scripts/scaffold_remotion.py <slug> --install` |
| Render is 0 seconds / black | `durationInFrames` 0 or all scenes `from == to` | Check `build_remotion_props.py` output for missing beats |
| Text renders in a fallback serif | `@fontsource` import missing from `Root.tsx` | Restore the import block from `assets/remotion/src/Root.tsx` |
| Audio drifts out of sync | `vo_master.wav` re-mastered after props were built | Rebuild props, then re-render |
| Chromium `GL` / `swangle` crash | no GPU on the runner | Keep `Config.setChromiumOpenGlRenderer('swangle')` |
| `invalidTags` on upload | tag string > 500 chars incl. quotes | Trim to ≤444 chars (see `thumbnail-and-metadata.md`) |
