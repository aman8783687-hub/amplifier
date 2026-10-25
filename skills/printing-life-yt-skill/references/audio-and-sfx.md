# Printing Life — Voice, Music and SFX

The channel sounds like a **deadpan friend explaining history in a pub**, not a
documentary narrator and not a hype YouTuber. The voice is the engine. Music and
effects exist to punctuate it, never to fill silence.

---

## 1. Casting the narrator

Default narrator:

| Setting | Value |
|---|---|
| Voice | `en-GB-RyanNeural` |
| Rate | `+0%` (occasionally `-2%` for serious acts) |
| Pitch | `+0Hz` |
| Volume | `+0%` |

Why: mid-low, dry, British, not theatrical. It can deliver "the king was
executed" and "the pig was fined" in the same tone, which is the joke.

### Narrator alternatives

| Voice | Feel | Use |
|---|---|---|
| `en-GB-ThomasNeural` | softer, older, avuncular | Origins, reflective endings |
| `en-GB-SoniaNeural` | crisp, sceptical | A female narrator series, if the owner wants one |
| `en-US-GuyNeural` | brighter, newsy | American-centred stories; use sparingly |
| `en-US-AriaNeural` | warm, wry | Character voices, not the main narrator |

Pick **one narrator voice per channel** and keep it. Changing narrator between
episodes resets the audience's relationship with the channel.

---

## 2. Character voices

The narrator also plays the characters, the way a storyteller does. Use small
rate and pitch shifts, not cartoon impressions.

| Character type | Voice | Rate | Pitch | Example |
|---|---|---|---|---|
| King / aristocrat | `en-GB-RyanNeural` | `-8%` | `-25Hz` | Louis XVI, George III |
| General / officer | `en-GB-ThomasNeural` | `-4%` | `-15Hz` | Napoleon, Wellington |
| Bureaucrat / clerk | `en-GB-RyanNeural` | `+6%` | `+10Hz` | ministers, tax officials |
| Aide / panic | `en-GB-RyanNeural` | `+10%` | `+25Hz` | messengers, advisers |
| Crowd / mob | `en-US-GuyNeural` | `+8%` | `+10Hz` | one line, shouted |
| Child | `en-GB-MaisieNeural` | `+4%` | `+10Hz` | young royals, street kids |
| Female lead | `en-GB-SoniaNeural` | `+0%` | `+0Hz` | queens, revolutionaries |

Rules:

- Maximum **four recurring voices** per episode, plus narrator and crowd.
- A character must sound the same in every scene. Put the preset in the script
  header once.
- Do not use accents to signal villainy or stupidity. It is lazy and it ages
  badly.
- If a character has one line, the narrator can read it. Do not cast a new voice
  for a single sentence.

Script header example:

```markdown
# VOICE NARRATOR: en-GB-RyanNeural | +0% | +0Hz
# VOICE LOUIS: en-GB-RyanNeural | -8% | -25Hz
# VOICE CLERK: en-GB-RyanNeural | +6% | +10Hz
# VOICE MARIE: en-GB-SoniaNeural | +0% | +0Hz
```

---

## 3. Writing for the voice

- **Short sentences.** If a sentence has three commas, cut it.
- **Full stops are timing.** edge-tts pauses at them; commas are faster.
- **Let the joke land.** Put the punchline in its own short line, then move on.
- **Avoid tongue-twisters and numbers in digits.** Write "twenty thousand", not
  "20,000". The voice reads digits inconsistently.
- **Names:** write the pronunciation you want phonetically if edge-tts mangles
  it, e.g. "Robes-pierre" or "Ver-sigh".
- **No stage directions inside the spoken line.** `(angry)` will be read aloud.
  Put emotion in the voice preset and the words.
- **One idea per scene.** If the line needs a breath, it needs a cut.

The pipeline inserts `0.12 s` lead-in, `0.18 s` between lines and `0.40 s`
tail per scene. That is enough. Do not add long silences in the script; they
read as dead air, not comedy.

---

## 4. Music

Music is **optional but recommended**. The channel's reference style uses a
comedic score; without it, the edit can feel like a slideshow. The rule is:
**music under narration, never over it.**

### Sourcing

Use only music you can license:

1. **YouTube Audio Library** — filter "attribution not required" where possible.
2. **Kevin MacLeod / Incompetech** — CC-BY, credit required in the description.
3. **Original or commissioned beds** — best long-term option.
4. **Pixabay / Free Music Archive** — check the licence on the track page, not
   the site's general claim.

Never use:

- OverSimplified's music or any track ripped from a YouTube video.
- Commercial film scores, game soundtracks, or "no copyright" reuploads.
- Anything you cannot name the licence of.

Keep a `music/LICENCES.md` with track, artist, source URL, licence and credit
line. If you cannot fill that row, do not use the track.

### Cue map

A 12-minute episode needs **4–6 cues**, not 40.

| Section | Music feel | Gain |
|---|---|---|
| Cold open | jaunty, curious, small ensemble | 0.14 |
| The world | warm, marching, moderate | 0.12 |
| The fuse | tense, ticking, low strings | 0.12 |
| Act turn / war | percussion, brass, urgent | 0.14 |
| The cost | sparse, sad, one instrument | 0.10 |
| The turn | triumphant or ominous | 0.13 |
| The bill | reflective, resolving | 0.10 |

Place cues with a `MUSIC:` line at the scene where they start:

```markdown
## s18 | chapter | The war begins
MUSIC: 03_march.mp3 | 0.13
CARD: THE WAR BEGINS | 1792
```

`assemble.py` keeps each cue running until the next `MUSIC:` line, fades it in
and out, and ducks it under the voice with a sidechain compressor. A global bed
is also supported:

```bash
python3 assemble.py script.md --workdir . --music music/bed.mp3 --music-gain 0.12
```

### Ducking

The pipeline uses:

```
sidechaincompress=threshold=0.03:ratio=10:attack=20:release=420
```

That means the music drops about 10 dB whenever the narrator speaks and recovers
in under half a second. If music is still fighting the voice, lower the gain
before touching the compressor.

---

## 5. SFX palette

Generated locally by `make_sfx.py`. No sample licensing, no YouTube rip.

| File | Length | Use | Gain |
|---|---:|---|---|
| `whoosh.wav` | 0.62 s | scene transitions, card exits | 0.35–0.5 |
| `boom.wav` | 1.20 s | cannon, slammed fact, title card | 0.5–0.7 |
| `thud.wav` | 0.35 s | body hits floor, door closes, book drops | 0.4–0.55 |
| `pop.wav` | 0.18 s | speech bubble, bright idea | 0.3–0.4 |
| `ding.wav` | 0.90 s | money, promotion, punchline | 0.25–0.35 |
| `sting.wav` | 1.10 s | threat, reveal, "this will not end well" | 0.4–0.5 |
| `riser.wav` | 1.50 s | build before a chapter card | 0.35–0.5 |
| `scratch.wav` | 0.55 s | record-scratch reality check | 0.35–0.45 |
| `stamp.wav` | 0.45 s | verdict, map claim, title slam | 0.45–0.6 |

Placement rules:

- **One effect per beat.** A boom plus a stamp plus a whoosh is noise.
- **Hit on the cut, not before it.** `at: 0.0` means the first frame of the scene.
- **Do not put SFX under every sentence.** Silence is a tool.
- **No laugh track, no applause, no cartoon boing on every step.**
- **War scenes:** cannon and musket at the turn, then pull the effects out for
  the cost. The absence does the emotional work.

```markdown
SFX: boom | 0.0 | 0.55
SFX: pop | 6.1 | 0.35
SFX: stamp | 6.15 | 0.5
```

---

## 6. Mix targets

| Element | Target |
|---|---|
| Narration | −16 to −12 LUFS short-term, peaks below −3 dBTP |
| Music | 12–18 dB below narration while speaking |
| SFX | 6–12 dB below narration; transient peaks may touch narration |
| Master | −14 LUFS integrated, −1.5 dBTP true peak |
| Channels | stereo, 48 kHz |
| Silence | no gap longer than 0.6 s inside a scene |

`assemble.py` applies `loudnorm=I=-14:TP=-1.5:LRA=11` on the final mix. If the
result sounds squashed, render at `-16` and check on phone speakers before
uploading.

### Phone test

Play the final on a phone speaker at 50%:

- Can you hear every word over the music?
- Do the booms distort?
- Does the quiet act still have presence?

If not, fix the mix, not the script.

---

## 7. Captions and accessibility

`voice.py` writes `captions.srt` with line-level cues. Use it for:

- YouTube captions (upload in Studio → Subtitles, or paste into the editor).
- A checked transcript in the description for search.
- Proofreading the narration before images are generated.

Do not burn karaoke-style word-by-word captions into the video. The channel's
look is clean; on-screen text is for cards, lower thirds, impacts and bubbles,
not for repeating the narrator.

---

## 8. Edge-TTS troubleshooting

`edge-tts` depends on Microsoft's online service. If synthesis fails:

1. **Retry.** Run the same `voice.py` command again; it resumes completed lines.
2. **Reduce concurrency.** `--jobs 1` avoids rate limits and flaky sockets.
3. **Update.** `pip install --user --upgrade edge-tts` (7.3.1 or newer).
4. **Check the network.** A websocket timeout to `speech.platform.bing.com` is
   usually a network/VPN/firewall issue, not a bad script.
5. **Change network.** Try another connection or a VPN exit in a supported
   region.
6. **Reuse what exists.** If lines are already recorded, `--reuse` rebuilds the
   timeline without re-synthesising.

Never fake a voice with a robotic local TTS for a published episode. Wait for
the service or record the narration manually. A bad voice wastes the entire
production run.
