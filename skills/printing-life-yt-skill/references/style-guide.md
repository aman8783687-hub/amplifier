# Printing Life — Visual Style Guide

The channel's look is **flat 2D historical cartoon**: thick ink outlines, solid
fills, oversized heads, period costumes, parchment maps and deadpan reaction
shots. It is the visual grammar popularised by OverSimplified, rebuilt with our
own palette, characters and assets.

**Rule zero:** never trace, crop, recolour or re-upload an OverSimplified frame,
character, logo, thumbnail, script or music track. The goal is the *language* —
clear-line cartoon history with comic timing — not a copy of their property.

---

## 1. Why the style reads the way it does

Five things do most of the work:

1. **Silhouette first.** A character must be recognisable as a black shape at
   thumbnail size. Hats, hair, crowns, epaulettes and bellies create silhouette.
2. **Thick uniform outline.** One dark ink colour, no variable line weight, no
   sketchy pencil noise. The outline is the brand.
3. **Flat fills, almost no shading.** One shadow tone at most. Gradients belong
   in skies and parchment, never on faces.
4. **Oversized heads, tiny bodies.** The face carries the joke; the body carries
   the costume. Head ≈ 42–48% of total figure height.
5. **Historical costume, modern emotion.** A powdered wig, a 1914 tunic or a
   Roman helmet, worn by a character who is visibly annoyed, smug or terrified.

At 1920×1080 a viewer should recognise the era from the costumes and props in
under one second, before the narrator says a word.

---

## 2. Locked palette

| Role | Hex | RGB | Use |
|---|---|---|---|
| Ink | `#211A14` | 33, 26, 20 | Every outline, most body text |
| Paper | `#F2E3C6` | 242, 227, 198 | Sky, parchment, card backgrounds |
| Paper dark | `#DECBA7` | 222, 203, 167 | Shadow bands, map borders, stains |
| Brick red | `#B03A2E` | 176, 58, 46 | Banners, blood-free drama, enemy territory |
| Red dark | `#80261E` | 128, 38, 30 | Red shadows, title-card rules |
| Mustard gold | `#D9A441` | 217, 164, 65 | Money, arrows, highlights, royal trim |
| Navy | `#2E4057` | 46, 64, 87 | Uniforms, night, water, cold states |
| Olive | `#6B7A4F` | 107, 122, 79 | Fields, maps, secondary uniforms |
| Sky | `#A8C3C9` | 168, 195, 201 | Distance, haze, neutral backdrops |
| Cream | `#FFF6E2` | 255, 246, 226 | Text on dark, speech bubbles |

**Discipline:** a scene may use ink + paper + two accents. Three accents maximum.
If a generated image comes back with teal, magenta, neon green or purple, reroll
it. Colour chaos is the fastest way to stop looking like the channel.

Skin is the one exception: natural skin tones are allowed, kept desaturated.
Never paint a real living person's likeness; every character is a cartoon.

---

## 3. Character design

### Proportions

- Head: 42–48% of the figure's height.
- Body: a rounded rectangle or pear, not a realistic torso.
- Arms and legs: simple tapered tubes, two joints maximum.
- Hands: mitten or four-finger block; never individual realistic fingers.
- Feet: rounded blocks or period shoes, slightly oversized.
- Eyes: two solid black dots, 8–14 px at 768×512. No whites, no irises.
- Eyebrows: the main acting tool. Thick, separate, able to float above the eyes.
- Nose and ears: usually absent. A big nose is a character choice, not default.
- Mouth: a short line, a small oval, or absent for deadpan. Never detailed lips.

### The costume anchor

Every named character gets **one costume anchor** that never changes, plus **one
prop**. Examples:

| Character | Silhouette anchor | Prop | Face |
|---|---|---|---|
| Louis XVI | tall powdered wig, wide blue coat, gold sash | handkerchief | droopy eyes, small mouth |
| Robespierre | tight powdered wig, green coat, high collar | spectacles | unblinking dot eyes |
| Napoleon | bicorne hat, grey greatcoat | rolled map | sharp brows, short mouth |
| A British officer | red coat, tall shako | swagger stick | moustache, permanent frown |
| A peasant | brown cap, patched tunic | pitchfork | tired brows, stubble dots |

Write these into the `# CAST` headers of every script and use `{NAME}` tokens in
`IMG:` prompts. The image model has no memory; the script does.

### Expression sheet

Generate these six faces once per recurring character, pick the best, and reuse
the same descriptor in prompts:

1. neutral / deadpan
2. smug
3. worried
4. furious
5. exhausted
6. screaming

Do not generate a new face design for every scene. Inconsistency reads as a
different character, not a different mood.

---

## 4. Backgrounds

Build backgrounds in three loose layers so the frame has depth without detail:

1. **Sky / back wall** — flat paper or sky tone, optional soft stain.
2. **Architecture** — one or two large shapes: a wall, window, tent, ship, map
   table, palace façade. Keep windows and doors empty of lettering.
3. **Foreground props** — one or two objects that tell the story: a cannon, a
   bread loaf, a ledger, a broken chair, a map with no labels.

Detail budget: about **20 strokes per background element**. If a palace needs
1,000 windows, draw a repeated window pattern as a texture, not individual panes.
Crowds are 3–7 simplified figures, not 100 faces.

Leave the **bottom 18% calm** (floor, table, empty ground). Lower thirds and
captions live there.

---

## 5. Shot types and prompt recipes

The subject line comes first, the style suffix is added by `gen_images.py`.
Keep prompts to one action and one or two props.

### A. Establishing wide

```
wide establishing shot of {PLACE}, {PERIOD ARCHITECTURE}, tiny figures in
period costume, one clear foreground prop, parchment sky, stage-play depth
```

Use for: a new country, a new act, a battle line, a city before/after.

### B. Two-shot argument

```
{CHARACTER A} and {CHARACTER B} facing each other in a heated argument,
opposite sides of the frame, clear gap between them, period costumes,
expressive eyebrows, one shared table between them
```

Use for: diplomacy, ultimatums, family betrayals, treaty signings.

### C. Close-up reaction

```
close-up of {CHARACTER}, head and shoulders, exaggerated {EMOTION} expression,
thick eyebrows, dot eyes, plain parchment background, one small prop at the edge
```

Use for: a punchline, a threat, a disastrous message. Cut to this, hold 1–2 s.

### D. Crowd / assembly

```
a crowd of six simplified people in {PERIOD} clothing, seen from behind,
facing a single speaker on a low platform, one raised fist, no individual faces
```

Use for: parliaments, riots, rallies, armies. Keep faces generic.

### E. Map plate

```
aged parchment map of {REGION}, flat unlabelled landmasses in muted olive and
cream, thick ink coastlines, simple mountain triangles, no text, no borders,
no compass rose lettering, top-down view
```

Never let the model write place names. `ARROW:` and `LOWER:` layers carry the
information.

### F. Object insert

```
single {OBJECT} on a plain parchment surface, dramatic side light, thick
outline, flat colour, no text, centred with generous empty space
```

Use for: a letter, a crown, a telegram, a loaf of bread, a severed head (kept
cartoon-bloodless), a treaty, a coin.

### G. Diagram / system

```
simple two-part diagram of {PROCESS}, left side labelled only by shape and
colour, right side showing the consequence, arrows suggested by composition,
no words, no numbers, flat cartoon
```

Because the image cannot letter, the narrator explains and the `IMPACT:` card
adds the one keyword.

---

## 6. Composition rules

- **16:9, 1920×1080.** Perchance outputs 768×512; `prep_frames.py` cover-crops.
- **Safe area:** keep faces and key props inside the central 80%. A 1.18 push-in
  crops ~9% per side; anything at the edge will leave the frame.
- **Bottom 18%** stays clean for lower thirds.
- **One idea per frame.** If the prompt contains "and" three times, split it.
- **Eye-line matters.** Leave room in the direction a character looks.
- **Opposing sides.** Put rivals on opposite thirds; do not centre both.
- **Scale for comedy.** A tiny king in a huge chair, a giant hat on a small
  general, a crowd dwarfed by a palace.

---

## 7. Text and cards

All lettering is rendered by `make_cards.py`. The image model is forbidden from
drawing words.

| Layer | Font | Treatment |
|---|---|---|
| Episode title | Anton | cream on brick-red band, ink stroke, red drop shadow |
| Part badge | Bebas Neue | gold plate, ink outline, below title |
| Chapter card | Anton | ink on parchment, gold sub-plate, thin double rule |
| Lower third | Bebas Neue | cream on ink box, gold left bar |
| Impact word | Anton | cream fill, heavy ink stroke, red starburst, −3° tilt |
| Speech bubble | Bebas Neue | cream rounded box, 7 px ink outline, pointed tail |
| Channel logo | Luckiest Guy | cream with ink stroke, bottom-right, −2° tilt |

Rules:

- Uppercase for cards and lower thirds. Sentence case only inside dialogue
  bubbles when the character is being casual.
- One impact word per beat. Two competing words cancel each other.
- Impact text is **1–2 words, 18 characters maximum**. A long phrase turns the
  starburst into a banner and covers the frame. Put the full phrase in the
  narration; the card carries the punch.
- Dates in lower thirds: `VERSAILLES, 1789`, not `May 5th 1789 at 3:15pm`.
- Never put an impact card or bubble on top of a chapter card. Cards are their
  own beat; effects belong over scene plates.

---

## 8. Motion grammar

The edit is a **limited-animation storyboard**, not a slideshow. Every scene gets
exactly one move:

| Move | Use | Feel |
|---|---|---|
| `in` | reveal, tension, a slow realisation | push-in, default |
| `out` | aftermath, isolation, a reveal of scale | pull-back |
| `left` / `right` | maps, marches, comparisons, scanning a room | lateral pan |
| `up` / `down` | hierarchy, falling, a tall object | vertical pan |
| `shake` | explosion, slap, cannon, "oh no" | 0.9 s of camera shake |
| `none` | cards, text-heavy frames, precise diagrams | locked-off |

Additional punctuation:

- **Hard cut** between scenes. No cross-dissolves; they kill comic timing.
- **Card slam:** title/chapter card appears on a `boom` or `stamp` SFX.
- **Bubble pop:** speech bubble appears with a `pop` SFX on the first word.
- **Arrow draw:** the arrow fades in over 0.3 s and holds. Do not animate a
  bouncing arrow; this is a map, not a PowerPoint.
- **Hold the reaction:** after a punchline, keep the close-up for 1.2–2 s with no
  new information. The silence is the joke.

---

## 9. Consistency workflow

1. Write the cast bible into the script headers (`# CAST LOUIS: ...`).
2. Generate **one character sheet per lead** before any scene plates. Pick the
   version with the strongest silhouette.
3. Copy the exact winning descriptor into the cast header. Do not paraphrase.
4. Use `IMG: {LOUIS} ...` tokens; `gen_images.py` substitutes the header text.
5. Generate two options per scene (`--variants 2`), keep the first, review
   `images2/alt/` before prep.
6. If a scene is busy or off-model after two rerolls, simplify the beat: fewer
   characters, one prop, or split the scene.

The model cannot count. "Three advisers" often produces five. Either accept the
crowd as generic or write "two advisers" and let the third be implied.

---

## 10. Style calibration (do this once per session)

Generate the same prompt in three presets and pick the closest:

```bash
cd <workdir>
python3 <skill>/scripts/gen_images.py script.md --workdir . --only s01 --style tintin --force
python3 <skill>/scripts/gen_images.py script.md --workdir . --only s01 --style comic  --force
python3 <skill>/scripts/gen_images.py script.md --workdir . --only s01 --style flat   --force
```

Move the winner to `images2/s01.jpg`, set `# STYLE:` in the script, and use that
preset for the whole episode. Never mix presets inside one video.

Calibration prompt to reuse:

```
IMG: a French king in a powdered wig and blue coat standing alone in a huge
empty hall of mirrors, one tiny servant in the distance, wide shot, deadpan
```

Judge on: outline weight, head size, amount of shading, period readability,
whether the bottom 18% is clean, and whether any text appeared (instant reject).

---

## 11. Common failures and fixes

| Failure | Cause | Fix |
|---|---|---|
| Text/letters appear | Model loves signage | Add "no text no letters no numbers" early, not only at the end; remove "map labels", "newspaper", "book cover" phrasing |
| Photoreal faces | Style too weak | Use `tintin`, add "chibi proportions, dot eyes, no nose", reroll |
| Scene looks like a poster | Too many elements | One action, one prop, split the beat |
| Character changes race/age | Descriptor drift | Use `{NAME}` token from cast header every time |
| Bottom crowded | Composition ignored | Add "empty floor in the bottom third", crop with `--crop-y 0.12` |
| Colours neon | Prompt drift | Add palette words and "muted historical palette"; reroll |
| Faces too small for thumbnail | Wide shot | Add a separate close-up plate for the thumbnail |
| Arrow covers a face | Arrow placed after generation | Place arrows in the empty third; check the frame before choosing coords |

---

## 12. Thumbnail formula

One idea, one threat, one title.

- Background: the most dramatic **scene plate**, darkened at the top and bottom.
- Characters: one or two, large, facing off or reacting. Cutouts are optional;
  a strong two-shot can carry it.
- Title: 2–4 words, Anton, gold fill, heavy ink stroke, top of frame.
- Part badge: red plate, bottom-left, `PART 1`.
- Logo: `Printing Life` plate, bottom-right.
- Contrast: the thumbnail must survive at 320×180. Squint test: can you read the
  title and see the conflict?

Avoid: full sentence titles, three characters, a busy battle, question marks,
red arrows pointing at nothing, and the word "history" as the main noun.

```bash
python3 <skill>/scripts/make_cards.py thumbnail \
  --bg images3/s04.jpg \
  --title "THE BREAD RIOT" \
  --part 1 \
  --kicker "1789" \
  --out final/thumbnail.jpg
```
