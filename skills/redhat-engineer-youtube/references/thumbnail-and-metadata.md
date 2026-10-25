# Thumbnail, title and metadata

Packaging decides whether the video gets watched. On a daily channel, it is the highest-leverage 30 minutes of the whole day.

## Thumbnail

**Locked template** (build once, fill daily):
- 1280×720, PNG.
- **Left third:** the host in the pose that matches the topic's emotion (Discovering, Curious, Explaining, Thinking). Same size and position every time.
- **Right two-thirds:** the topic's hero object as a bold silhouette or simple illustration — the transistor, the bomb, the container, the chip.
- **Text:** 2–4 words maximum, huge, heavy sans-serif, white with one word in `#E60000`. Never a full sentence. Never a title repeat.
- **Background:** deep near-black (`#111111`) with faint techy doodle elements. Consistent across every video — this is what makes a RedHat Engineer thumbnail identifiable in a sidebar.
- **Never:** shocked-face clickbait, red arrows and circles, five colours, small text, anything touching the frame edge (the timestamp overlays the bottom-right corner).

**Text formulas that work:** the contradiction ("TOO SMALL TO SEE"), the stake ("$3 TRILLION IDEA"), the impossible part of the build ("BUILT BY HAND"), the scale ("5,000 YEARS LATE").

**Legibility test:** scale to 210×118 px and look at it. If the words aren't readable and the object isn't identifiable at that size, redo it. Also check it against a dark and a light UI background.

Once the channel has enough traffic, use YouTube's built-in thumbnail Test & Compare on videos where two concepts genuinely differ — and feed the winner's pattern back into the template.

## Title

- Keep it under 60 characters so it isn't truncated on mobile.
- Front-load the interesting word; the last third of a title often gets cut.
- One clear idea, no ALL CAPS, no more than one piece of punctuation.
- The title must be a promise the video keeps. Overpromising buys one click and loses a subscriber.

**The title format is fixed (since 2026-10-03):** `How [X] Was Built`, or `How [X] Are Built` when the thing is still made today. Examples: "How Fighter Jets Are Built", "How the Panama Canal Was Built", "How the First Microchip Was Built".

- Use the plain name people search for ("Fighter Jets", not "Supersonic Combat Aircraft").
- Add nothing else: no "| RedHat Engineer" suffix and no subtitle. The hook goes on the thumbnail.
- Because the title is fixed, the **thumbnail text carries the curiosity**: the stake, the scale or the impossible part of the build ("MACH 2 BY HAND", "50,000 PARTS", "BUILT TO CRASH"). It must not repeat the title.

Write three candidate thumbnail texts and pick one; log the rejected ones for a later Test & Compare.

## Description

```
[1–2 sentence hook restating the video's promise, containing the main search term naturally.]

[3–4 sentences on what the video covers.]

⏱️ Chapters
0:00 [Hook line]
0:xx [Section]
...

📚 Sources
- [Source name] — [URL]
- ...

🎩 RedHat Engineer: how the things that run the modern world were built, one story at a time.
Subscribe: [channel URL]

▶️ Watch next: [most relevant previous video + link]
📂 Series playlist: [link]

#hashtag1 #hashtag2 #hashtag3
```

The agent cannot look up channel or playlist URLs: leave out the `Subscribe`, `Watch next` and `Series playlist` lines rather than writing `[link]` placeholders; the operator adds them when posting.

Chapters need at least three timestamps and the first must be 0:00. Sources in the description are a real credibility signal on a history-of-technology channel — never skip them.

## Tags and metadata

The agent writes the tags and the fields in `metadata-and-delivery.md`; the playlist, end screen, pinned comment and other YouTube Studio settings below are done by the operator when posting.

- 8–15 tags: the exact topic, 2–3 synonyms, the series name, plus format terms (technology history, explained, documentary, animation).
- Set the video to **Not made for kids**.
- Set language and caption language; upload the `.srt`.
- Add to the series playlist and to the "All Episodes" playlist.
- End screen: subscribe element + one specific next video (the most-related previous episode) + the series playlist.
- Pinned comment: a one-line extra fact or an honest "what I couldn't fit in" plus a question that invites replies. Post it immediately after publishing — early comment activity is worth having.
- Set the altered/synthetic content disclosure honestly (see `compliance-and-safety.md`).

## Format B (cinematic) packaging differences

Format B does **not** use the `How [X] Was Built` title or the host pose template. It is
search-led, so packaging follows the reference video that proved the format
(`references/cinematic-format.md` has the full reasoning):

- **Title:** `The Psychology of [X] (Why You [Specific Failure])`, 45–55 characters.
  The first clause is the exact search phrase; the parenthetical is the curiosity gap.
  Rejected candidates get logged in `metadata.json` → `title_candidates_rejected`.
- **Thumbnail:** the operator's own art, used exactly as supplied at 1280×720. Do not
  regenerate it, do not add a RedHat Engineer logo, do not change the wording. Check it at
  210×118 only.
- **Description:** hook → what the research says (named researchers and years) → the
  tactics → personal closing → chapters → linked sources → synthetic disclosure →
  not-medical-advice disclaimer → 3 hashtags.
- **Tags:** 444 characters max including YouTube's quotes around multi-word tags. Over 500
  returns `invalidTags` and rejects the whole upload; 15–20 tags fits.
- **Chapters:** six, from the `kicker` fields, so they must match the on-screen labels.
