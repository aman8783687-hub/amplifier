---
name: Wild Thinking YouTube Video Builder
description: End-to-end builder for engaging YouTube explainer videos in the "Wild Thinking" style. Use when the user wants to create a full video (script, voice, images, subtitles, sound effects, overlays) for the Wild Thinking channel or similar explainer channels. Produces a 4-6 min 1080p MP4 with dynamic Ken Burns zoom, animated word-by-word subtitles, whoosh SFX, no background music, and real image/meme overlays.
---

# Wild Thinking YouTube Video Builder

Builds a complete, upload-ready YouTube explainer video from a topic. Pipeline:

1. **Script** — research-backed, question title, 8-12 min target, chapters.
2. **Voice** — Edge-TTS at 1x with inter-sentence pauses removed (comma technique).
3. **Images** — Perchance AI (cinematic watercolor style, landscape).
4. **Subtitles** — ASS word-by-word animated (fade-in + upward slide, yellow highlight for key words).
5. **Dynamic edit** — Ken Burns zoom + fade-in per scene.
6. **Overlays** — real photos/memes from the internet, centered, larger, fade in/out.
7. **SFX** — whoosh at every scene transition + ding at end, **no background music**.
8. **Final** — concat + loud, clear audio.
9. **Upload** — publish to the single target channel (default: `Wild Thinking`) via the Amplifier bridge.
10. **Analytics** — read per-video and channel stats back from Amplifier.

## Inputs needed
- Topic (e.g., "What Did Ancient Humans Do When Someone Died?")
- Channel name (default: Wild Thinking)
- Optional: specific meme/photo overlays the user wants.

## Step 1 — Script
Write a script with:
- Title in question form ("What Did Ancient Humans Do When Someone Died?")
- Hook (first 30s): confirm click, open uncloseable question, prove payoff exists.
- 8-12 chapters, each 2-4 sentences. Mark `[ON SCREEN: ...]` per beat.
- "RESEARCH & SOURCES" section with real papers/books.
- Outro CTA (one ask).
- Save narration per chapter to `audio/seg01.txt` ... `audio/segNN.txt` (one file per scene, 2-4 sentences each, ~10-20s spoken).

Rules:
- Never invent numbers/sources.
- 150 words/min runtime estimate.
- Avoid long pauses: keep sentences short.

## Step 2 — Voice (1x, no gaps)
For each segment, replace sentence-ending ". " with ", " to remove TTS inter-sentence pauses, then synthesize at 1x:

```bash
cd <workdir>
for i in $(seq -w 1 N); do
  n="seg$(printf '%02d' $i)"
  text=$(sed 's/\. /, /g' "audio/$n.txt")
  uvx edge-tts --text "$text" --write-media "audio/$n.mp3" --write-subtitles "audio/$n.srt" --voice en-US-GuyNeural
done
```

This keeps word speed at 1x but removes the long silences between sentences.

## Step 3 — Images (Perchance)
Use the perchance-image-generation skill. Adapt `scripts/generate.py` with one subject per segment. Style: cinematic watercolor gouache, loose ink linework, muted earthy palette, 16:9 landscape. Output to `images2/segXX-*.jpg`.

Run:
```bash
env -u PYTHONHOME -u PYTHONPATH python3 gen_images.py 0 N
```

## Step 4 — Animated subtitles (ASS)
Build per-segment ASS from the SRT using `scripts/build_ass.py`. It creates word-by-word fade-in + upward slide, yellow highlight for key words/numbers.

Key words list is in `build_ass.py` (IMPORTANT set). Edit per topic.

## Step 5 — Dynamic edit (Ken Burns zoom)
For each segment, create a clip with slow zoom + fade-in + burned subtitles:

```bash
for i in $(seq 1 N); do
  n=$(printf "seg%02d" $i)
  img=$(ls images2/${n}*.jpg | head -1)
  ffmpeg -y -loop 1 -i "$img" -i "audio/$n.mp3" \
    -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -r 30 \
    -vf "zoompan=z='min(zoom+0.0008,1.18)':d=900:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,scale=1920:1080,subtitles=audio/$n.ass,fade=t=in:st=0:d=0.25" \
    "clips/seg$n.mp4"
done
```

## Step 6 — Overlays (real images/memes from the internet)
Source images (Wikimedia Commons `Special:FilePath/...` is copyright-safe; Imgflip `i.imgflip.com/....jpg` for memes). Download with `curl -sL`. Overlay centered, larger, with fade:

```bash
# per-clip overlay (avoids full-video truncation)
ffmpeg -y -i clips/segXX.mp4 -loop 1 -i overlay.jpg \
  -filter_complex "[1:v]scale=520:-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1,fade=t=out:st=DUR-0.4:d=0.4:alpha=1[ov];[0:v][ov]overlay=(W-w)/2:(H-h)/2[ovv]" \
  -map "[ovv]" -map 0:a -c:v libx264 -preset fast -crf 20 -c:a copy -shortest clips_ov/segXX.mp4
```

Choose overlay moments at pattern interrupts (surprising facts, new chapters). Keep on screen 2-8s.

## Step 7 — SFX (no background music)
Mix a whoosh at every scene transition (start of each clip except first) + a ding at the end. Use iterative mixing with `-nostdin`:

```bash
# extract base audio
ffmpeg -y -i <final_video> -vn -acodec pcm_s16le -ar 44100 -ac 2 /tmp/base.wav
# compute transition times from clip durations, mix whoosh at each
# (see scripts/mix_sfx.py)
```

Use `weights=1 0.3:normalize=0` to keep voice loud and whooshes subtle.

## Step 8 — Final concat + remux
```bash
# concat clips
python3 -c "import glob; files=sorted(glob.glob('clips/seg*.mp4')); open('concat.txt','w').write(''.join(\"file '%s'\n\"%p for p in files))"
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final_no_sfx.mp4

# remux with SFX audio
ffmpeg -y -i final_no_sfx.mp4 -i /tmp/mixed.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k final.mp4
```

## Step 9 — Upload to the target channel (Amplifier bridge)

The user connects all channels once in the Amplifier dashboard
(https://amplifier-sand.vercel.app). Uploading is **per target channel**: pick
the channel by name and only that channel receives the video.

Default target: **Wild Thinking** (`--channel` / `AMPLIFIER_CHANNEL`).

The agent key lives at `~/.config/amplifier/agent_key` (or `AMPLIFIER_API_KEY`).
Do not print it.

```bash
cd <workdir>
SKILL_DIR=~/.claude/skills/wild-thinking-yt-skill
python3 "$SKILL_DIR/scripts/upload_to_amplifier.py" \
  --video final/<name>.mp4 \
  --thumbnail final/thumbnail.jpg \
  --metadata-file final_upload_metadata.txt \
  --channel "Wild Thinking"
# add --privacy public to publish immediately; default is private for review
```

`final_upload_metadata.txt` should contain `Title:`, `Description:`, `Tags:`
(comma-separated) and optionally `Privacy:`. Explicit flags such as
`--title`, `--description-file`, `--tags` override the file.

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

Before a real upload, validate the target channel, key, and metadata with
`--dry-run` (mints a token but uploads nothing). Add `--analytics --wait 60`
to print initial stats in the same run.

## Step 10 — Analytics

After upload (views/likes need a little time to appear):

```bash
python3 ~/.claude/skills/wild-thinking-yt-skill/scripts/amplifier_analytics.py \
  --channel "Wild Thinking" --range 28d
```

- Per-video: `--video <amplifierVideoId>` (from Step 9 output).
- Whole account: `--overview`.
- Force a fresh pull from YouTube first: add `--refresh` (throttled to 15 min
  per video by the API).

The skill should report totals (views, likes, comments, watch minutes, subs
gained) and the per-video breakdown, not just raw JSON.

## Output files
- `final/<name>.mp4` — 1080p, 4-6 min
- `final/thumbnail.jpg` — 1280x720 with title overlay
- `final_upload_metadata.txt` — title, description, chapters, tags

## Bundled scripts
- `scripts/gen_images.py` — Perchance bulk image generator (edit SUBJECTS).
- `scripts/build_ass.py` — SRT → animated ASS converter.
- `scripts/mix_sfx.py` — iterative whoosh mixer.
- `scripts/upload_to_amplifier.py` — upload the finished video to one target channel + register for analytics.
- `scripts/amplifier_analytics.py` — channel/video/overview analytics.

## Notes
- Never use background music (user preference).
- Always verify clip durations match audio after each encode.
- If an overlay is invisible, check that `-loop 1` is set on the image input.
- Re-encode per-clip (not whole video) for overlays to preserve full duration.
- Upload goes to **one** channel only (the `--channel` target). Do not fan out
  to every connected channel; the other connections exist for authentication.
- Default privacy is `private`. Pass `--privacy public` only when the user asked
  for the video to go live immediately.
- Never print or commit the agent key.
PY