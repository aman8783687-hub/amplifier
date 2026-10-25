# Edit and assembly

`scripts/assemble_episode.py` does the whole edit; there is no manual timeline. This page says what it produces so you can judge the result and write scripts that fit it.

## What assembly does

1. Renders each `05_scenes/scene_XXXX.png` into a clip with a slow Ken Burns push in or out (`zoompan`, about 6% over the scene). The scene stays on screen from its `start` in `timings.json` until the **next** beat's start, so the section-break silences are covered by picture. Direction comes from the shotlist's `motion` field, else it alternates.
2. Joins the scenes end to end. There is **no intro sting and no outro card** (removed 2026-09-26): the video opens on the first hook beat at 0:00 and ends on the last scene.
3. Builds the sound-effects bed (`build_ambience.py`, see `ambience-sound.md`: a soft whoosh on every cut, a reveal sting at the TURN, a few keyword effects), mixes it `ambience.bed_db` under the narration (`03_audio/vo_master.wav`), and masters the mix to `audio.target_lufs` with the true-peak limit from `channel_state.json`. There is **no music bed** (removed 2026-10-03). The cue list is written to `07_edit/ambience_plan.resolved.json`.
4. Encodes 1920x1080, 24 fps, H.264 high profile, CRF 22 capped at `format.video_maxrate`, AAC stereo, to `07_edit/redhat-engineer-<slug>-1080p.mp4`. This is the only copy of the render; `08_publish/` holds the thumbnail, metadata and delivery record and never a second copy of the video.
5. Burns in animated word-by-word captions (`build_captions.py` → `07_edit/captions.ass`, from `03_audio/word_timings.json`; see `captions.md`).
6. Writes `07_edit/captions.srt` from the script text with timings straight from `timings.json` (no shift, since nothing is spliced in), as a sidecar caption track for YouTube.

There is no background music, and no intro/outro cards, transition cards or colour grade in this pipeline. `--no-ambience` / `--no-captions` turn the two layers off for one render.

## Writing for this assembly

- The script still uses the [HOOK] [SETUP] [ESCALATION] [TURN] [LANDING] sections (they pick the voice preset), and the **first line of the hook is a question**.
- Average shot length 6–9 seconds; nothing over 12. Cut on beats in the narration.
- The section-break "breath" (about a second of silence before each new section) comes from `stitch_audio.py`; the picture holds on the previous scene through it.
- The first 30 seconds carry disproportionate weight in whether the video works: the video opens cold on the hook question, with no branding ahead of it.

## Final QC before delivery

`deliver_episode.py` checks size, audio and runtime automatically. Also check by eye (contact sheets are fine):

- [ ] No missing scenes, no scene that outlives its narration, no dead air
- [ ] Every scene has Ken Burns motion; nothing sits as a flat static hold
- [ ] Character on-model throughout; palette clean, red uniform across scenes
- [ ] Burned-in captions match the audio and sit clear of the frame edge (grab a few frames with `ffmpeg -ss <s> -i <mp4> -frames:v 1 f.png`)
- [ ] Effects stay under the voice: no whoosh or sting masks a word

If the video is *wrong* (factual error, broken audio, off-model scenes), fix it and re-run assembly; do not deliver it. If an episode cannot be fixed at all, give up on it with `python3 scripts/state_db.py episode-abandon "<slug>" "<why>"` and start a new one.
