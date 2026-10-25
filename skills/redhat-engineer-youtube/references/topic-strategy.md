# Topic strategy

## What belongs on this channel

One innovation per video, told as a story with stakes. The subject can be 5,000 years old or five months old. The test: *can I explain why the world was different after this thing existed?* If the answer is only "it's cool tech", the topic isn't ready — find the tension.

## The build-journey format (channel format since 2026-10-03)

Every episode is **How X Was Built**: one thing, and the whole journey of how humans got it built. It replaces the mystery lens (2026-09-26 to 2026-10-03). The promise to the viewer is the same every time: *by the end you'll know how this thing went from impossible to everywhere.*

A topic is ready only when you can name all five of these:

1. **The problem that demanded it.** What was so costly, dangerous or impossible that people had to build this?
2. **The first attempts and why they failed.** Real dead ends, crashes, bankruptcies, wrong ideas. This is the most watchable part, so a topic with no documented failures is weak.
3. **The breakthrough moment.** One specific event a stickman can act out (Otis cutting the rope, the first barcode scan in 1974, the first jet flight).
4. **How it is actually built.** The real build process or the key mechanism, told as steps a viewer can picture (materials, parts, assembly, testing).
5. **Where it ended up.** How the thing is made or used today, and what it changed.

Good topics are physical, hard-won builds with a clear turning point: fighter jets, the jet engine, the microchip, the Panama Canal, the Hubble telescope, undersea internet cables, GPS satellites, Roman aqueducts, skyscrapers, the lithium-ion battery. Avoid topics that were only gradual improvement with no turning point, and topics that are pure software with nothing a stickman can build.

Disputes, rivalries and legends (who really built it first, the myth versus the record) are still welcome, as **beats inside the journey**, not as the frame of the video. The integrity rules stay: no invented quotes, unsourced legends labelled as such. See `compliance-and-safety.md`.

Weapons and military hardware (fighter jets, rockets): tell the engineering and the build, at an encyclopaedic level. No targeting, armament or performance details beyond public overviews, and no glorifying of combat. See SKILL.md's "When to stop and ask".

## Operator-pinned topic

If a queued topic has `"pinned": true`, make it next, before scoring anything else. As of 2026-10-03 the pinned first episode of the new format is **How Fighter Jets Are Built**.

## Series (pillars)

Group every video into one of five series. Series give the channel shape, make playlists work, and give returning viewers a reason to binge.

1. **Foundations** — the ancient and industrial bedrock: wheel, writing, concrete, printing press, steam, steel, electricity, the assembly line.
2. **The Machine Age** — computing and electronics: transistor, integrated circuit, microprocessor, the internet, GPS, the smartphone, GPUs.
3. **Power & Peril** — energy and its dark twin: nuclear fission, the bomb, the grid, solar, batteries, fusion.
4. **Invisible Infrastructure** — the things nobody notices: shipping containers, standard time, the barcode, TCP/IP, undersea cables, the Haber–Bosch process.
5. **Right Now** — present-day innovation: transformers and LLMs, gene editing, robotics, space launch economics, brain–computer interfaces.

Rotate series across the week so the channel never feels like it's stuck on one theme, but run occasional 3–5 video arcs when a chain of inventions tells a bigger story (vacuum tube → transistor → chip → GPU → AI).

## Scoring a candidate topic

Score 1–10 on each, average them, and queue anything ≥ 7.0:

- **Demand** — are people already searching for or watching this? Check YouTube search suggestions, competing videos' view counts, and whether existing coverage is old or bad.
- **Story** — does the build journey have a real problem, real failures and one breakthrough moment (the five-point test above)?
- **Visual** — can stickmen and simple diagrams carry it? Abstract software concepts are harder than physical machines; find the metaphor before committing.
- **Freshness** — is there an angle nobody else is using? "The invention of X" is crowded; "the mistake that gave us X" is not.
- **Fit** — does it sound like a RedHat Engineer video?

## Gap-finding routine (run weekly)

1. Search YouTube for your next 10 candidate topics. Note the top 3 videos each: views, age, length, thumbnail style, and what they *miss*.
2. Look for topics where the best existing video is over 3 years old or under 100k views on a high-demand term — that's an opening.
3. Read comments on competitors' videos for "I still don't understand…" — those become your hooks.
4. Refill the bank so it never drops below 30 queued topics.

## Seed bank (60 to start)

**Foundations:** the wheel · controlled fire · the plough · writing · the arch · Roman concrete · the water wheel · the compass · the printing press · the mechanical clock · the telescope · the steam engine · interchangeable parts · the Bessemer process · the assembly line · the electric motor

**The Machine Age:** the telegraph · the telephone · the vacuum tube · the transistor · the integrated circuit · the microprocessor · the hard disk · the mouse and the GUI · ARPANET · TCP/IP · the World Wide Web · the lithium-ion battery · the smartphone · the GPU · cloud computing · the camera sensor

**Power & Peril:** the light bulb · the power grid · alternating current · the internal combustion engine · nuclear fission · the atomic bomb · the nuclear reactor · the solar cell · the wind turbine · fusion research · the electric car

**Invisible Infrastructure:** the shipping container · standard time zones · the barcode · GPS · the Haber–Bosch process · pasteurisation · vaccination · anaesthesia · the elevator brake · air conditioning · undersea cables · the ATM · double-entry bookkeeping as a technology

**Right Now:** the transformer architecture · large language models · CRISPR · mRNA vaccines · reusable rockets · autonomous driving · quantum computing · brain–computer interfaces

## Rules

- No topic repeats within 120 days.
- If a video badly underperforms, note *why* in `reports/changelog.md` — was it the topic or the packaging? Don't retire a good topic for a bad title's sake.
- When a topic overperforms, immediately queue a sibling topic in the same series and a follow-up angle within 10 days.
