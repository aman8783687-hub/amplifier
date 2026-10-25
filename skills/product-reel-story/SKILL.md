---
name: product-reel-story
description: >
  Make a finished 9:16 product reel from a shopping product URL — scrape the real
  product assets, write a six-beat first-person voiceover, synthesize voice + score,
  build it in Remotion with word-synced typography, QA stills, render, verify, and
  package the publish metadata. Use when asked for "a reel for this product",
  "make a video like this for <product link>", "turn this product into a Shorts/Reel",
  or when a product page and a target platform are given. Works for any commerce
  site, not just Myntra.
---

# Product Reel — Story Edition

Turn one product page into a 40–60 s vertical reel that feels like a person
telling you about something they found, not a shop selling it.

Output contract (do not drift from this unless the user asks):

| | |
|---|---|
| Format | 1080×1920, 30 fps, H.264 + AAC 192k, yuv420p |
| Length | 40–60 s, **derived from the voice track**, never a guessed constant |
| Loudness | −14 LUFS integrated, true peak ≤ −1.5 dBFS |
| Visual | one product, film grain + halation, editorial type, designed text per scene |
| Audio | one voice, one procedural underscore, 2–3 accent sounds |
| Also deliver | cover/still, post caption, publish metadata |

Read the whole file before starting. The phases are ordered because each one
feeds the next — voice timings are the single source of truth for all timing.

---

## 0. Prerequisites (check, install only what is missing)

```bash
node --version        # 20+
ffmpeg -version
python3 -c "import numpy; print(numpy.__version__)"
uv --version          # used for edge-tts; pip fallback is fine
```

`edge-tts` needs no key but does need network. If it is unavailable, any TTS with
**word-level timestamps** works — swap the plugin, keep the pipeline.

---

## 1. Product intel — get facts, not vibes

```bash
mkdir -p product_<id>
```

Collect from the **live page**, never from memory:

- product name, brand, product id
- price and MRP (compute the discount; do not trust a badge)
- material, length, what is included, care instructions
- occasion the audience actually shops it for, and the nearest date-driven event
  (festival, wedding season, exam season, sale) with its real date
- 1–2 concrete detail claims you can *see* in the photos (border work,
  stitching, print repeat, hardware) — these become the obsession beat

Write `product_<id>/product_info.json`:

```json
{ "productId": 0, "brand": "", "name": "",
  "price": { "mrp": 0, "discounted": 0 },
  "url": "", "images": [], "videos": [],
  "facts": { "material": "", "included": "", "care": "", "occasion": "", "date": "" } }
```

**Rule:** every number and claim in the script must trace to this file or to a
photo you actually looked at. If a fact is missing, cut the line — do not invent.

## 2. Assets — headed browser, real page

Headless gets blocked on most large commerce sites. Use a headed persistent
Playwright profile (Firefox or Chromium), accept the cookie wall, let lazy
images settle, then read the page's own state object.

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    ctx = p.firefox.launch_persistent_context("./.browser", headless=False)
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    # scroll to force lazy loads
    for _ in range(8):
        page.mouse.wheel(0, 900); page.wait_for_timeout(350)
    data = page.evaluate("window.__myx?.pdpData ?? null")   # site-specific; fall back to DOM
    html = page.content()
    page.close(); ctx.close()
```

Practical notes:

- **Images:** grab the page's real asset URLs, then request the largest variant.
  Many CDNs take transform prefixes (`h_2160,q_90,w_1620`); stripping them gives
  the original upload. Save both HD and original if they differ.
- **Video:** PDP videos are usually a hosted player (Brightcove, Cloudinary,
  Kaltura). Read its playback API or network calls for the progressive MP4 and
  download it — signed URLs expire, so keep the local file as the source of truth.
- **Poster frame** for every clip, from the player or `ffmpeg -ss 1`.
- **Verify each file exists and opens** (`ffprobe`, PIL). A 0-byte or HTML-error
  "jpg" is the most common silent failure.
- **Drop brand cards.** Product galleries end with "about us" / size-chart /
  similar-products cards. Look at every image and keep only this product.
- Build `gallery.html` (thumbnails, dimensions, download links) so the user can
  review assets without opening a folder. It is cheap and always appreciated.
- Upscale a soft product video before using it full-bleed:
  `ffmpeg -i in.mp4 -vf "scale=1440:-2:flags=lanczos,unsharp=5:5:0.6:5:5:0.0" -crf 18 out.mp4`

**If assets are thin** (3 photos, no video): lean on macro crops, slow pushes and
full-bleed type. Never fabricate a shot that does not exist.

## 3. Story — six beats, first person, no ad grammar

Write the voiceover *before* the visuals. Six segments, one emotion each,
mapped to a fixed arc:

| # | Beat | Job | Length |
|---|---|---|---|
| 1 | **Curiosity** | An overheard sentence. Product half-hidden. Ends on a promise. | 5–7 s |
| 2 | **Obsession** | One specific detail, examined too closely. Three short nouns. | 7–9 s |
| 3 | **Desire** | The thing moves / drapes / catches light. Raise the body. | 6–9 s |
| 4 | **Disbelief** | The price, spoken plainly. A breath before it. | 5–7 s |
| 5 | **Inspiration** | Two lives, one object. "Morning… night… same thing." | 7–9 s |
| 6 | **FOMO** | The date, the regret, one instruction. Stop. | 8–11 s |

Hard rules that separate this from a sale creative:

- First person, spoken aloud, contractions, no brand name in the voice.
- The brand appears **only** on the end card. No logo animation, no "shop now".
- Numbers are spoken as words ("one thousand three hundred forty-five"), and
  written as digits on screen.
- No `STOP`, no `81% OFF`, no `SIZES MOVING FAST`, no starbursts, no emoji.
- No karaoke captions. Each scene owns its typography, revealed on its own words.
- One CTA, platform-correct: "the link's in the pinned comment" (not "link in bio"),
  or "saved to the highlights", etc. Ask the platform, not the habit.
- Beat 4 must have **silence** before the price — 1.2–1.6 s of near-nothing.

Sanity-check the read time: ~2.6 words/second at `+9%` rate. If a beat needs more
than its slot, cut words, never rush the tempo.

## 4. Voice + timings — the spine of the build

Use `edge-tts` with a warm regional voice and ask for **WordBoundary** events.
Store every segment and every word time; all animation reads from this file.

```python
# scripts/gen_voice.py
import asyncio, json, os, subprocess, edge_tts

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # reel/
AUD  = os.path.join(BASE, "public/audio")
VOICE, RATE, PITCH, TEMPO, GAP, FPS = "en-IN-NeerjaExpressiveNeural", "+9%", "-2Hz", 1.03, 0.34, 30

SEGS = [("s1", "..."), ("s2", "..."), ("s3", "..."), ("s4", "..."), ("s5", "..."), ("s6", "...")]

async def synth(name, text):
    raw = os.path.join(AUD, f"{name}_raw.mp3")
    c = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")
    words = []
    with open(raw, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"text": ch["text"], "start": ch["offset"]/1e7, "dur": ch["duration"]/1e7})
    out = os.path.join(AUD, f"{name}.mp3")
    subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",
                    f"atempo={TEMPO},loudnorm=I=-16:TP=-1.5:LRA=7",
                    "-ar","48000","-b:a","192k", out], check=True)
    os.remove(raw)
    for w in words:                       # timestamps must follow atempo
        w["start"] = round(w["start"]/TEMPO, 3); w["dur"] = round(w["dur"]/TEMPO, 3)
    return out, words
```

Then lay the segments end to end with `GAP` between them and write
`src/timeline.json`:

```json
{ "fps": 30, "voice": "...", "totalSeconds": 0.0, "totalFrames": 0,
  "segments": [ { "id": "s1", "text": "...", "file": "audio/s1.mp3",
                  "start": 0.0, "duration": 0.0, "startFrame": 0, "frames": 0,
                  "words": [ { "text": "...", "start": 0.0, "dur": 0.0 } ] } ] }
```

`totalSeconds = sum(durations) + GAP*(n-1) + 1.0` tail.
Print each segment's duration as you go; if a beat overruns its slot, fix the
script now, not the animation later.

## 5. Score — an underscore, not a track

Synthesize it with numpy. No licensed audio, no loops, nothing that needs a credit.

- Bed sits **~11.5 LU under the voice at rest**, ~14–15 LU under while speaking:
  voice −16.0 LUFS, bed −27.5 LUFS.
- Duck is soft: −3.2 dB, 120 ms attack, 550 ms release, smoothed — a hard step
  pumps on a sustained drone.
- No shaker, no four-on-the-floor. Only a low pulse in two beats and a heartbeat
  in the curiosity beat.
- One low impact + one soft bell at the price; one bell at the deadline line.
- Whooshes low-passed to ~3 kHz and quiet (~0.07), or transitions "swish".
- EQ for a phone speaker: `lowshelf f=110 g=-2.5, highshelf f=380 g=3.5, lowpass f=7000`.
- Add a short convolution tail (2 s noise IR, 16% wet) so it feels like a room.
- 1.2–1.6 s duck to ~6% right before the price cue; ramp in/out over 350 ms.
- Master in ffmpeg: measure with `loudnorm … print_format=json`, then a second
  pass with `linear=true` so nothing pumps. Target `I=-14:TP=-1.5:LRA=11`.

Anything with a hook, a drop or a chime stack will make the cut read as a promo.
Delete it.

## 6. Remotion build

Scaffold if needed: `npm create video@latest`. Keep dependencies at Remotion 4.

```
src/timeline.json          generated — never hand-edited
src/lib/cues.ts            timing helpers; TOTAL_FRAMES from timeline.json
src/lib/theme.tsx          palette + type stack + shared decoration
src/scenes/S1Curiosity.tsx … S6Fomo.tsx
src/components/Film.tsx    Grain, Halation, Kicker, Quote, Rule
src/components/UI.tsx      Price, StrikePrice, KenImg, Scrim
src/Reel.tsx               <Audio>, <Sequence> per segment, film layer, progress
public/images/  public/video/  public/fonts/  public/textures/grain.png
```

`cues.ts` — the only place timing math lives:

```ts
import timeline from "../timeline.json";
export const FPS = timeline.fps;
export const SEGMENTS = timeline.segments;
export const SEG: Record<string, any> = Object.fromEntries(SEGMENTS.map((s) => [s.id, s]));
export const TOTAL_FRAMES = timeline.totalFrames;

/** absolute seconds of the n-th occurrence of a spoken word */
export const cue = (id: string, word: string, occurrence = 0): number => {
  const seg = SEG[id]; if (!seg) return 0;
  const target = word.toLowerCase().replace(/[^a-z0-9-]/g, "");
  let seen = 0;
  for (const w of seg.words) {
    if (w.text.toLowerCase().replace(/[^a-z0-9-]/g, "") === target) {
      if (seen === occurrence) return seg.start + w.start;
      seen++;
    }
  }
  return seg.start;
};
export const local = (absSec: number, sceneStartSec: number) =>
  Math.round((absSec - sceneStartSec) * FPS);
```

`Reel.tsx` — sequences are derived, never typed in:

```tsx
<Audio src={staticFile("audio/soundtrack.mp3")} />
{SEGMENTS.map((seg, i) => {
  const next = SEGMENTS[i + 1];
  const dur = (next ? next.startFrame : TOTAL_FRAMES) - seg.startFrame;
  const Comp = SCENES[seg.id];
  return <Sequence key={seg.id} from={seg.startFrame} durationInFrames={dur}><Comp start={seg.start} /></Sequence>;
})}
```

Composition: `width={1080} height={1920} fps={FPS} durationInFrames={TOTAL_FRAMES}`.

Visual language that reads as editorial rather than commercial:

- Film layer over everything: moving grain (`backgroundPosition` offset by frame),
  one warm screen-mode halo top-centre, one vignette. Opacity ~0.06 grain.
- Type: one expressive serif italic for emotion, one small-caps sans for labels,
  one condensed display face for numbers only. Load fonts locally via
  `@font-face` + `staticFile`, and `delayRender`/`continueRender` until
  `document.fonts.ready` — otherwise the first frames fall back.
- Text is designed per scene and keyed to its own spoken words
  (`spring({ frame: frame - local(cue("s2","mirror"), start) })`).
- Vertical safe areas: keep type out of the bottom 320 px (platform UI) and
  use a bottom scrim, not a caption bar.
- Ken Burns on stills: `scale(1.46 → 1.26)` across the scene, never a still frame.
- Progress: a 2 px hairline, not a loading bar.
- Cross-scene continuity: one palette, one gold, one type scale. Different scene
  layout, same film.

## 7. QA stills before you render the whole thing

```bash
node scripts/render_stills.mjs 20 300 620 950 1200   # one bundle, many frames
```

Look at every still, at full size, and check:

- Does the frame read at phone size? Squint — if the product is unrecognisable, recrop.
- Text is not on a face, a hand, or the product's own busy detail.
- No two elements collide (price + badge + quote). No cut-off type at the edges.
- The promised detail from the script is actually visible at that moment.
- Scene one hides the product enough to create curiosity.
- End card: price, one CTA line, brand small. No CTA competing with the price.

Fix, re-render stills, repeat. Only then run the full render.

```bash
npx remotion render src/index.ts <CompositionId> out/<name>.mp4 \
  --codec=h264 --crf=21 --pixel-format=yuv420p \
  --audio-codec=aac --audio-bitrate=192k --concurrency=4
```

## 8. Verify the delivered file, not the code

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate \
  -show_entries format=duration -of default=nw=1 out/<name>.mp4
ffmpeg -hide_banner -nostats -i out/<name>.mp4 -af loudnorm=print_format=json -f null - 2>&1 | tail -20
ffmpeg -hide_banner -i out/<name>.mp4 -vf blackdetect=d=0.2,freezedetect=n=0.003:d=1 -f null - 2>&1 | grep -E "black_|freeze"
ffmpeg -ss 100 -i out/<name>.mp4 -frames:v 1 out/check/f100.png
```

Then prove sync: pick three moments, read the expected phrase out of
`timeline.json`, extract the frame, and confirm the words on screen are those
words. Duration must equal `totalSeconds` (±0.1 s); audio must not be clipped at
the tail — that is what the +1 s tail frame budget is for.

## 9. Publish package

Produce alongside the video:

```
out/<name>.mp4
out/cover.png            or a 1280×720 still for the thumbnail slot
out/post_caption.txt     platform-native caption, hook on line 1, CTA last line
out/youtube_description.txt (when the target is YouTube)
```

Metadata rules:

- Title: product + the number the audience filters by
  (`This ₹1,345 Diwali saree doesn't look like ₹1,345`). No ALL CAPS spam.
- Description: first 2 lines carry the search phrase and the price band, then
  what it is, then chapters, then the CTA. Front-load, don't bury.
- Chapters: first at `0:00`, **every chapter ≥ 10 s** — one 9 s chapter makes
  YouTube drop the whole list. Verify by diffing consecutive timestamps.
- Tags: 15–20, mixing intent (`saree under 1500`), category, brand, occasion.
- Category: match the content (Howto & Style 26, Education 27, People & Blogs 22).
- Thumbnail: 1280×720, JPEG < 2 MB. Unverified channels get custom thumbnails
  rejected — expected, not a failure; say so plainly.
- Upload private, verify processing and metadata via the API, then flip public.

## 10. Pitfalls that cost a full render

| Symptom | Cause | Fix |
|---|---|---|
| `React error #300` at one exact frame | early `return` placed before a hook (`useMemo`) | all hooks first, return after |
| Frame flashes white / next cut paints over | un-clamped `interpolate` | `extrapolateLeft/Right: "clamp"` everywhere |
| Audio tail clipped | duration hardcoded, script changed | derive `TOTAL_FRAMES` from `timeline.json` |
| Type jumps on frame 0 | fonts not awaited | `delayRender` + `document.fonts.load(...)` |
| Text overflows a phone screen | designed at desktop preview scale | inspect stills at 1080×1920, check longest word |
| Everything looks like an ad | score within ~5 LU of voice, groove + chimes | loudness split + remove rhythm |
| Scene feels like a product card | still image + border + logo | full-bleed crop, grain, no frame |
| Render dies after 30 min | one bad frame | test the boundary frame as a still first |
| Voice and captions drift | timestamps not rescaled after `atempo` | divide word times by tempo |
| CDN images are HTML errors | hotlink blocked / transform URL wrong | verify with PIL, use the page's own asset URL |

## Definition of done

- [ ] `product_info.json` facts match the live page; every script claim traces to it
- [ ] Images/video open locally; brand cards removed; gallery built
- [ ] Six beats present, one CTA, no sale-badge vocabulary in voice or on screen
- [ ] `timeline.json` regenerated from the final voice; nothing hardcoded
- [ ] Score ≥ 11 LU under the voice, no groove, no chime stack
- [ ] Stills reviewed at full size; collisions and crops fixed
- [ ] Delivered file: 1080×1920, 30 fps, −14 LUFS, TP ≤ −1.5, duration matches audio
- [ ] Sync proven at three timestamps by extracting frames from the **rendered** file
- [ ] Cover/still, caption, metadata and (for YouTube) valid ≥10 s chapters written
- [ ] Report anything not done — especially uploads, which need explicit approval
