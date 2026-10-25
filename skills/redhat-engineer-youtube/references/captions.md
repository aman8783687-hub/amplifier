# Captions

Ported from the Imagine Error pipeline on 2026-10-03. Burned-in, animated word-by-word captions
(white, black outline, the spoken word popped in brand red `#E60000`). `07_edit/captions.srt` is still
written alongside (one cue per beat) to upload as a YouTube caption track. `--no-captions` on
`assemble_episode.py` skips the burn-in.

Pipeline: edge-tts WordBoundary events -> `generate_narration_chunks.py`
`.wordbounds.jsonl` -> `stitch_audio.py` remap -> `word_timings.json` ->
`subtitles/segment.py` phrase grouping -> `subtitles/ass_builder.py`
styled ASS -> `build_captions.py` writes `captions.ass` ->
`assemble_episode.py` burns via libass `subtitles` filter.

Why ASS over SRT/drawtext: native animation via `\t`/`\c`/`{\r}` override
tags (the "pop and highlight" per-word animation).

Config knobs live in `channel_state.json`'s `captions` block: font,
size, colors (`&H00BBGGRR` ASS byte order), alignment (2 = bottom-anchor)
+ `margin_v_ratio` (0.12; a 16:9 video has no platform UI over the bottom
of the frame to clear), word/line
limits, gap threshold, pop animation timing.

Known limitation: timing can drift up to
roughly 100ms by a chunk's end due to `loudnorm`'s internal buffering —
deemed acceptable.

Testing loop: `python3 scripts/build_captions.py <slug>` (fast, no
re-encode) to inspect `.ass` directly; always look at actual rendered
frames before trusting a style change (full `assemble_episode.py` run +
`ffmpeg -ss <s> -i ... -frames:v 1 frame.png`).
