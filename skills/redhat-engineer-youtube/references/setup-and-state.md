# State

`channel_state.json` is the single source of truth for anything that must not drift; MongoDB holds the topic bank and the small text state that has to survive between GitHub Actions runs.

## `channel_state.json`

Locked config, loaded by every script through `scripts/state.py`'s `load_state()`:

- `voice`: edge-tts voice id and the per-section rate/volume/pitch presets (`hook`, `setup`, `escalation`, `turn`, `landing`), chunk limits.
- `style_lock`: the image prompt suffix, aspect `16:9`, resolution `1920x1080`, reference dataset, generation notes.
- `audio`: loudness target (-14 LUFS), true peak, silence-trimming values, gaps. `music` is `"none"`: videos have no music bed.
- `format`: runtime target and hard range (`target_runtime_range_seconds`, 300-420), words per minute, scene length, fps, zoom, `video_maxrate`.
- `counters`: `episodes_made`, bumped once per episode by `deliver_episode.py`.

Anything that must be identical across videos lives here, not in your head and not as a second copy inside a script or doc. Any change to a locked value gets a dated line in `reports/changelog.md` with the reason. If a value in state contradicts what you were about to do, state wins.

## MongoDB (database `redhat_pipeline`)

`scripts/state_db.py` is the only interface:

| Command | Does |
|---|---|
| `topics [queued\|used\|rejected]` | list topics (default queued) |
| `topics-count` | how many topics per status |
| `topic-add` | add queued topics: a JSON object or list on stdin, each needing `topic` and `pillar` (one of the five series) plus `series`, `score`, `angle`, `visual_hooks` |
| `topic-use "<name>"` | queued -> used, stamped with today's date |
| `topic-reject "<name>" "<why>"` | -> rejected |
| `recent [N]` | recently made episodes with status |
| `pull` / `push` | run start / run end (the workflow's `run_cycle.sh` does both) |

Collections: `topics`, `episodes` (script, shotlist, chunk plan, metadata, `01_research/sources.md`, `08_publish/delivery.json` for each episode), `state` (`channel_state`), `slots`.

At the start of a run `pull` rebuilds `channel_state.json` and restores the text files of unfinished episodes; an empty database is seeded once from `seed/topic_bank.seed.json` and `channel_state.json`. At the end `push` saves counters and episode text. Only text is stored: audio, images and video never go to the database.

Environment (set as GitHub Actions secrets, or in a local `.env` for `make-video`): `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` (optional `CLOUDFLARE_IMAGE_MODEL`), `MONGODB_URI`. Nothing is committed to git by the pipeline.

## Experiment ledger (`reports/experiments.md`)

One row per experiment, one variable live at a time:

```
| # | Start date | Variable changed | Hypothesis | Videos | Result | Keep? |
```
