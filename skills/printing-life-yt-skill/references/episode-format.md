# Printing Life — Episode Format

The channel tells **one big history story per episode**, in the voice of a
friend who has read the books and cannot believe what these people did. The
facts are real. The telling is simplified, comic and chronological.

---

## 1. The four formats

| Format | Length | Scenes | Use | Examples |
|---|---|---:|---|---|
| **Main story, Part 1** | 10–14 min | 55–75 | A famous war, revolution or empire with a natural break | The French Revolution, The Crusades, The American Civil War |
| **Main story, Part 2** | 12–16 min | 65–85 | Consequence and climax | The Terror, The Fall of Rome, Reconstruction |
| **Mini-War** | 6–9 min | 35–50 | A ridiculous small conflict with a big consequence | The Pig War, The Emu War, The War of the Bucket |
| **Profile** | 8–12 min | 45–65 | One ruler, con man or fanatic | Henry VIII, Rasputin, a fraudulent prince |
| **Origin** | 8–12 min | 45–60 | How an everyday object or system changed power | The printing press, the telegraph, the passport |

A new channel should not open with a six-part epic. Ship **Mini-Wars and
Profiles first**: they are finishable, they prove the format, and their titles
are curiosity machines. Earn the right to the 40-minute epic.

---

## 2. Runtime math

Narration runs about **150 words per minute** at the channel's pace.

| Target | Words | Scenes at 8–10 s |
|---|---:|---:|
| 7 min | 1,050 | 45–52 |
| 10 min | 1,500 | 62–75 |
| 12 min | 1,800 | 75–90 |
| 15 min | 2,250 | 90–110 |

A 12-minute episode is **75–90 scenes**, not 30. Each scene is one image, one
camera move, 7–12 seconds of narration. If a scene runs 20 seconds, it needs a
second visual or a cutaway.

Do not count words in your head. Write the script, run `voice.py`, read the
timeline duration, and cut or add scenes before generating images.

---

## 3. The beat sheet

Percentages are of final runtime. The numbers are a guardrail, not a religion.

| Beat | % | What happens | Visual |
|---|---:|---|---|
| **Cold open** | 0–6% | A comic scene with the eventual subject, before any context. A petty argument, a birth, a stupid decision, a man measuring a pig. | Close-ups, one location, no maps |
| **Title card** | 6–8% | Title + Part number. Music sting. | `title` card |
| **The world** | 8–22% | Who, where, why it mattered. The map. The balance of power. One absurd detail that makes the era human. | Establishing wides, map, crowd |
| **The fuse** | 22–38% | The specific grievance, insult, debt or ambition that starts the story. This is the *promise of the title*. | Two-shots, close-ups, object inserts |
| **Act I turn** | 38–42% | The first decision that cannot be undone. Chapter card. | Card + `boom` |
| **The mess** | 42–62% | Things escalate. Alliances, mistakes, battles, betrayals. Two or three set pieces. | Maps, crowds, reaction shots |
| **The midpoint reversal** | 62–66% | The plan fails, the ally switches, the king flees. The audience's assumption is broken. | Close-up + `sting` |
| **The cost** | 66–82% | The price. Sieges, famine, terror, dead ends. Slow the jokes; keep one running gag alive. | Crowds, ruins, object inserts |
| **The turn** | 82–92% | The decisive move. The battle, the vote, the execution, the treaty. | Map arrows, impact cards |
| **The bill** | 92–100% | What it actually changed, who paid, what it created. One sentence the viewer remembers. Optional next-episode hook. | Wide aftermath, final card |

### Chapter cards

A 10–14 minute episode carries **3–5 chapter cards**, roughly every 2–3 minutes.
Each is a clean paper card with a short phrase, not a table of contents:

- `THE THREE ESTATES`
- `THE BREAD PROBLEM`
- `THE GREAT FEAR`
- `THE MAN FROM CORSICA`

Never number chapters I–IV unless the episode is explicitly a list. The cards
are act breaks, not a syllabus.

---

## 4. The cold open

The first 30 seconds decides whether the video is recommended. Do **not** open
with a map, a date, a definition or "in this video". Open with a person doing
something small, and let the huge consequence be the joke.

### Five reliable recipes

1. **The petty cause.** Two officials argue about a pig, a bucket, a football
   match or a border tax. The narrator deadpans: "This would cost 600,000 lives."
2. **The birth parody.** A famous leader is born already wearing a uniform,
   already giving a speech, already disappointing his father.
3. **The bad idea.** A king looks at a map and says the sentence that starts the
   war. Cut to the map. Cut to his adviser's face.
4. **The bureaucracy.** A clerk stamps a form. The stamp starts a famine. The
   clerk goes to lunch.
5. **The impossible demand.** A messenger reads a treaty term so insulting that
   the room goes silent. One character laughs. Nobody else does.

### Cold-open rules

- One location, two or three characters, no narrator exposition for the first
  15 seconds if possible.
- The subject's name can wait. The *situation* cannot.
- End the cold open on a hard cut to the title card, not a fade.
- The title card lands with a `boom` or `stamp`.
- Do not use the cold open to explain the whole episode. It is a promise, not a
  summary.

---

## 5. Two-part structure

Split when the story has a natural **point of no return**, not at an arbitrary
halfway mark.

**Part 1** covers:

- the world before,
- the grievance,
- the first escalation,
- the point where compromise becomes impossible.

End Part 1 on a decision, not a battle. The last line should make Part 2 feel
inevitable: "And so, in the spring of 1792, France declared war on almost
everyone. It went about as well as you would expect."

**Part 2** opens with a **30–60 second recap** made of 5–8 quick shots from Part
1, narrated in the present tense. Do not replay whole scenes. Then a new title
card: `PART 2`.

Rules:

- Each part must stand alone for a viewer who starts there, but reward the viewer
  who watched both.
- Part 1 carries the discovery; Part 2 carries the payoff. Put the stronger
  thumbnail on Part 1.
- Do not announce "this is a two-parter" in the title. The `(Part 1)` suffix is
  enough.
- Never split a Mini-War. Mini-Wars are one sitting.

---

## 6. Humour rules

The comedy comes from **character, bureaucracy and contrast**, not from facts
being wrong.

### Use

- **Anachronistic comparison, not anachronistic fact.** "The treaty was 40 pages
  long, which in 1648 was basically a terms-and-conditions update."
- **Understatement.** A city burns. The narrator: "The neighbours were not
  thrilled."
- **Bureaucratic absurdity.** Committees, titles, forms, inheritance law,
  protocol. History is mostly paperwork with explosions.
- **Visual irony.** A character says "this is fine" while the background is on
  fire.
- **Running gags.** Two or three per episode, escalating. Aides who agree with
  everything. A messenger who is always shot. A king who cannot open a door.
- **Callbacks.** A joke from the cold open returns at the climax with a new
  meaning.

### Never

- Jokes that make a real atrocity funny. You may explain a massacre; you may not
  score a punchline off the victims.
- Punching down at a nationality, religion, ethnicity, disability or the poor.
- Slurs, sexual content, or jokes about children in danger.
- Invented quotes presented as real. If a line is dramatised, the narrator must
  signal it: "He probably said something like..."
- "Both sides were just as bad" when the record is clear. Nuance is fine;
  false balance is not.
- Glorifying a dictator, scammer or war criminal. Explain the appeal; do not sell
  it.

Tone target: **PG-13**. A 12-year-old can watch it; an adult does not feel talked
down to.

---

## 7. Accuracy workflow

"Simplified" means the *structure* is simplified. The facts stay true.

1. **Research file** — `research.md` in the episode folder. One section per act.
2. **Two sources per major claim** — a scholarly book, a university page, a
   museum, a primary source collection. Wikipedia is a finding aid, not a source.
3. **Date discipline** — every date that appears on screen must be checked.
4. **Quote discipline** — only quote words that exist in a source. Paraphrase
   everything else.
5. **Number discipline** — casualty figures get a range and a source in the
   research file. On screen: "around 20,000", never a fake precise number.
6. **Composite characters** — if you merge three advisers into one, say so in the
   research file and never give the composite a real person's name.
7. **Sensitive scenes** — no graphic imagery. Suggest with a closed door, a
   silhouette, a list of names, or a reaction shot.

A fact-check pass is a required step, not a nice-to-have. One invented "fun
fact" can poison the comments and the channel's credibility.

---

## 8. Scene rhythm

- **New visual every 7–12 seconds.** A cut, a push-in, a card, a bubble, an
  arrow. The viewer should never stare at the same frame for 15 seconds.
- **Major turn every 90 seconds.** A betrayal, a death, a battle, a reversal, a
  reveal.
- **Joke every 30–45 seconds** in the light sections; every 60–90 seconds in the
  serious ones.
- **Hold the reaction.** After a punchline, one beat of silence on a face.
- **One idea per scene.** If the narration has two ideas, use two images.
- **Chapter cards are breaths.** Put them after a turn, not in the middle of one.

---

## 9. Scene script example

```markdown
## s14 | scene | The bread march
IMG: {LOUIS} in a powdered wig and blue coat standing at a tall palace window,
looking down at a crowd of six simplified women in rough dresses, one holding a
loaf of bread, wide shot, hall of mirrors behind him, parchment light
MOVE: out
LOWER: VERSAILLES, 5 OCTOBER 1789 | 0.4 | 3.8
NARRATOR: The women of Paris had walked twelve miles to ask their king for bread.
LOUIS: Tell them we are... out of bread.
BUBBLE: LOUIS | 0.64,0.28
SFX: pop | 6.1 | 0.4
IMPACT: OUT OF BREAD | 6.2 | 1.6
SFX: stamp | 6.15 | 0.5
NARRATOR: This was not the reassuring answer they had hoped for.
```

Notice:

- one image, one action;
- a lower third carries place and date;
- a bubble and an impact punctuate the punchline;
- the next scene can cut to the crowd without a transition.
