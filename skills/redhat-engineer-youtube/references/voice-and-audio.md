# Voice and audio

Audio is the half of video that viewers forgive least. A great-looking video with muddy narration gets closed in twenty seconds.

## The chunking rule — read this twice

**Never generate more than ~30 seconds of speech in a single TTS call. Aim for 1–3 sentences per generation, 10–25 seconds.**

Why this matters: text-to-speech models degrade over long generations. Volume drifts downward, articulation smears, pacing accelerates or stalls, and artifacts creep in near the end of long outputs. Short generations stay in the model's sweet spot, and — just as importantly — when one chunk comes out wrong you regenerate 15 seconds instead of 8 minutes.

So a 7-minute video is roughly **35–60 separate generations**. That is normal and correct. Do not "optimise" by batching them into longer calls.

## Generation procedure

This channel's actual TTS provider (edge-tts, locked in `channel_state.json`) is driven by a local script, not a browser or a per-chunk manual call — but the chunk *plan* itself is something you write, not something a script infers:

1. Group the numbered beats from `02_script/script.md` into chunks of ~65 words or less (~28s at 140wpm), splitting on natural sentence breaks — a chunk can span more than one beat. Write the plan to `03_audio/chunk_plan.json`:
   ```json
   { "note": "...", "chunks": [ { "id": 1, "beats": [1, 2], "text": "..." } ] }
   ```
2. Run `python3 scripts/generate_narration_chunks.py <episode-slug>` from `RedHatEngineer/`. It synthesizes every chunk locally via edge-tts, using `channel_state.json`'s locked `voice.voice_id` and picking that chunk's rate/volume/pitch from `voice.settings.section_presets` by narrative section — no browser automation, no separate call per chunk to orchestrate by hand. Output lands as `chunk_0001.mp3`, `chunk_0002.mp3`, … in `03_audio/`. It's safe to re-run: existing chunk files are skipped, so fixing one bad chunk is just deleting that file and running the script again.
3. **QC every chunk before moving on:**
   - Full text present, nothing dropped or repeated.
   - No clipping, no digital artifacts, no sudden volume shift.
   - Technical terms and proper nouns pronounced correctly.
   - Peak level in the same range as the previous chunks.
   Regenerate any failure by deleting that chunk file and re-running the script — the section preset stays as locked, but a persistent bad read is usually fixed by lightly rewording the sentence (respelling hard names phonetically often works: "Oppenheimer" → "Oppen-hymer").
4. Never accept a "close enough" chunk. It will be the one thing a commenter mentions.
5. Once every chunk exists, run `python3 scripts/stitch_audio.py <episode-slug>` — see Stitching below.

## Stitching

1. Trim leading/trailing silence from each chunk to ~50 ms, and strip any *internal* dead air within a chunk longer than ~0.35s (TTS occasionally over-holds on a comma or em-dash). `stitch_audio.py` does this with `silenceremove=stop_periods=-1`, which removes every occurrence above the threshold while leaving natural short pauses untouched — the voice keeps its rhythm, it just never sits on silence. This is what keeps the finished video from feeling like it's wasting the viewer's time.
2. Insert deliberate gaps rather than butting clips together:
   - Within a paragraph: 250–400 ms
   - Between beats: 450–700 ms
   - Between sections / before a big reveal: 800–1200 ms
   Silence is pacing. A beat of nothing before the payoff line does more than any sound effect.
3. Crossfade seams by 15–30 ms to kill clicks.
4. Listen to the full stitched pass end to end at least once. You are listening for seams, not for content.

## Mastering the voice track

- High-pass filter at 80 Hz.
- Light de-esser if the voice is sibilant.
- Gentle compression (≈3:1, slow attack) for consistency across chunks.
- Loudness-normalise the **final mix** to −14 LUFS integrated, true peak ≤ −1 dBTP.
- Export `03_audio/vo_master.wav` (48 kHz, 24-bit).

## timings.json — the spine of the whole edit

While stitching, write out the timing map. Everything downstream cuts to this file.

```json
{
  "total_seconds": 447.2,
  "chunks": [
    { "id": 1, "beat": 1, "text": "This lump of glass and metal...", "start": 0.0, "end": 4.8, "section": "HOOK" },
    { "id": 2, "beat": 2, "text": "And in nineteen forty-seven...", "start": 5.25, "end": 9.9, "section": "HOOK" }
  ]
}
```

If total runtime lands outside 5:00–7:00, fix it in the script and regenerate — never by speeding up or slowing down the audio.

## Music

**None.** Since 2026-10-03 videos carry the narration only, with no background music: the operator found the bed distracting. `assemble_episode.py` masters `vo_master.wav` together with the quiet sound-effects bed (see `ambience-sound.md`; added 2026-10-03), which is not music. Do not add a music track back without the operator's explicit decision (log it in `reports/changelog.md`). The old track and `brand/music_licences.md` are kept for the record but unused.

## Final audio check

Play the finished mix on phone-grade output at low volume. If any word is unclear, fix it now. With no music, any dead air is fully exposed, so listen for gaps too. Most viewers are on a phone speaker in a noisy room.
