# Diwali Saree Reel — Remotion build

9:16 story reel for the Anouk embellished satin saree (Myntra product 41573047).

**Output:** `out/diwali_saree_reel.mp4` — 1080×1920, 30 fps, 47.9 s, H.264 + AAC.
**Cover:** `out/cover.png` · **Caption:** `out/post_caption.txt`

## The arc

This is not a sale creative. It is a first-person story that happens to end at a product.
The voice never says the brand; Anouk appears only on the end card.

| Time | Emotion | Voice | Visual |
|---|---|---|---|
| 0–6.2 s | Curiosity | "There's a saree that makes people stop mid-sentence. Not the one you're thinking of." | Fabric macro, no product reveal; the model arrives only on the second line |
| 6.2–14.9 s | Obsession | "I zoomed in on the border for ten minutes. Mirror. Sequins. Gold thread that catches the light." | Four macro push-ins with a `ZOOM ×2.4 → ×8.0` HUD and film-strip dots |
| 14.9–23.0 s | Desire | "Then I saw it move. Satin that falls like water. The kind of drape that makes you stand taller." | The only moving shot: rampwalk at 0.72×, warm grade, two serif lines |
| 23.0–29.8 s | Disbelief | "So I checked the price. One thousand three hundred forty-five. For this." | Near-silence, then a quiet ivory price; no badge, no starburst |
| 29.8–38.0 s | Inspiration | "Morning pooja, one way. Night party, a completely different woman. Same six yards." | Split panel, morning vs night, "same six yards." band |
| 38.0–47.9 s | FOMO | "Diwali is on the eighth. The one you'll wish you'd bought when it's gone. The link's in the pinned comment. Go." | Poster end card: stacked 8 / NOVEMBER, portrait, quiet underlined "link in the pinned comment" |

### What was deliberately removed

- The `STOP` slam and the price in the first three seconds.
- The pink `81% OFF` badge, `YOU SAVE`, `SIZES MOVING FAST`, the gold `LINK IN BIO` pill.
- `DETAIL 01/03` and the `DIWALI 2026 · FESTIVE DROP` chip.
- Karaoke captions. Every scene carries its own designed text, synced to the spoken words.
- The brand card `07.jpg` (it is an Anouk "about us" card, not this product).

### What was added

- Film grain (`public/textures/grain.png`) and a warm halation/vignette pass over every scene.
- Editorial type: Playfair italic for emotion, Inter small-caps for labels, Anton only for numbers.
- A 2 px gold progress hairline (retention cue, not a loading bar).
- A 1.5 s near-silence in the score before the price, then one low impact.

## Files

```
src/timeline.json          word-level voice timings (generated, 6 segments)
src/lib/cues.ts            timeline helpers; TOTAL_FRAMES derived from timeline.json
src/scenes/S1Curiosity.tsx
src/scenes/S2Obsession.tsx
src/scenes/S3Desire.tsx
src/scenes/S4Disbelief.tsx
src/scenes/S5Inspiration.tsx
src/scenes/S6Fomo.tsx
src/components/Film.tsx    Grain, Halation, Kicker, Quote, Rule
src/components/UI.tsx      Price, StrikePrice, KenImg, Scrim
src/lib/theme.tsx          palette + type stack
public/images/             product stills 01–06 (07 is a brand card, unused)
public/video/              rampwalk_1440.mp4 (upscaled + sharpened), listview.mp4
public/textures/grain.png  256×256 noise plate
public/audio/              per-line TTS + soundtrack.mp3 (voice + score, −14 LUFS)
scripts/gen_voice.py       edge-tts (en-IN-NeerjaExpressiveNeural, +9%, −2 Hz) + timings
scripts/gen_audio.py       procedural score (drone/pads/heartbeat, no shaker groove), mix + master
scripts/render_stills.mjs  fast still previews from one bundle
```

## Rebuild

```bash
# 1. voice + timings (needs uv / edge-tts)
uv run --with edge-tts python scripts/gen_voice.py

# 2. score + final mix
python3 scripts/gen_audio.py

# 3. preview stills
node scripts/render_stills.mjs 60 300 530 780 1000 1200

# 4. render
npx remotion render src/index.ts DiwaliSareeReel out/diwali_saree_reel.mp4 \
  --codec=h264 --crf=21 --pixel-format=yuv420p --audio-codec=aac --audio-bitrate=192k \
  --concurrency=4
```

## Facts used (from the live PDP)

- Price ₹1,345, MRP ₹6,999 → 81% off, save ₹5,654.
- Saree 5.5 m + 0.8 m unstitched blouse piece; satin, embroidered border, dry clean.
- Diwali / Lakshmi Puja 2026: Sunday 8 November.
- Music and SFX are synthesized locally (no licensed tracks); voice is Microsoft Edge TTS.

## Audio balance

The score is an underscore, not a track. It is deliberately quiet and rhythmless so
nothing about the cut reads as a sale creative.

- Voice normalised to −16.0 LUFS, score to −27.5 LUFS → ~11.5 LU apart at rest,
  ~14–15 LU apart while she speaks (soft −3.1 dB duck, 120 ms attack / 550 ms release).
- No shaker or four-on-the-floor groove; only a low pulse in s2 and s6, and a
  heartbeat in s1. Transition whooshes are low-passed and dropped to ~0.07 gain.
- One soft bell at the price, one at "gone" — the chime stack is gone.
- Score EQ'd for phone speakers (`lowshelf −2.5 dB @110 Hz`, `highshelf +3.5 dB @380 Hz`,
  `lowpass 7 kHz`) so the drone does not disappear on a phone.
- 1.5 s bed drop before the price cue is kept; the impact is 0.34, not a slam.
- Master: two-pass `loudnorm` with `linear=true` (no pumping) → −14 LUFS, TP −2.1 dBFS.
