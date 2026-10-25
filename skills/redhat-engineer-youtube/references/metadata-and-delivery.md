# Metadata and delivery

The pipeline never posts to YouTube. It ends with a verified video that is uploaded automatically to Content Lab (the operator's site: Cloudinary storage plus a listing in the RedHat Engineer section), together with the title, description and tags from `metadata.json`; the operator downloads it there and posts by hand. On GitHub Actions the workflow also attaches the files to the run as a fallback artifact (14 days); locally they stay in the episode folder.

## `08_publish/metadata.json`

Write it before running `run_episode.py`. Fields:

| Field | Rule |
|---|---|
| `title` | Required (delivery fails without it). Format A: always `How [X] Was Built` / `How [X] Are Built`. Format B: `The Psychology of [X] (Why You [Specific Failure])`. Under 60 characters, no channel suffix (see `thumbnail-and-metadata.md`). |
| `format` | `"cinematic"` selects Format B (Remotion render, 600-960 s runtime). Omit it for Format A (the default). |
| `description` | The full YouTube description from `thumbnail-and-metadata.md`: hook, summary, chapters (first at 0:00, at least three), sources (from `01_research/sources.md`), channel line, hashtags last. **Chapter timestamps** come straight from `timings.json` `start` times (no offset: there is no intro sting). |
| `tags` | 8-15 tags. |
| `thumbnail_text` | 2-4 words, uppercase. Without it no thumbnail is made. |
| `thumbnail_accent_word` | One word from `thumbnail_text`, drawn in `#E60000`. |
| `made_for_kids` | `false`. |
| `synthetic_disclosure` | `true` (the operator answers YouTube's altered/synthetic-content question accordingly). |

## What "done" means

`scripts/deliver_episode.py` (the last stage of `run_episode.py`) checks and records:

- `metadata.json` has a title;
- `07_edit/redhat-engineer-<slug>-1080p.mp4` exists, is non-empty, is 1920x1080 and has audio;
- the runtime is inside the format's range: `format.target_runtime_range_seconds` (300-420 s) for Format A, or `format_cinematic.runtime_range_seconds` (600-960 s) when `metadata.json` says `"format": "cinematic"`.

It writes `08_publish/delivery.json` (`status: ok`, or `failed` with the list of problems).

## The Content Lab upload

Right after a successful delivery check, `run_episode.py` runs `scripts/publish_content_lab.py <slug>`:

1. `POST {CONTENT_LAB_URL}/api/videos/sign` returns signed Cloudinary parameters.
2. The video goes straight to Cloudinary (never through the website).
3. `POST {CONTENT_LAB_URL}/api/videos` registers the title and a `youtube` block (title, description, tags, plus the `RedHat Engineer` tag) under project `redhat-engineer`.

It is idempotent (the slug is the key) and only uploads an episode whose `delivery.json` is ok. The result goes to `08_publish/upload_log.json` (`content_lab.status` is `ok` with the video URL, or `failed` with the error). When `CONTENT_LAB_URL` and `CONTENT_LAB_API_KEY` are set (always in CI), `pending_episodes.py` treats an episode as done only when the delivery check AND the upload are ok; without them (a local run with no `.env`) the upload is skipped and delivery alone is enough.

If the upload fails, read the error in `upload_log.json`, fix the cause (network, key, Cloudinary error) and re-run `python3 scripts/publish_content_lab.py <slug>`. Files over `CONTENT_LAB_MAX_MB` (default 100, Cloudinary's single-upload limit on the free plan) are refused before uploading: lower `format.video_maxrate` in `channel_state.json` (for example `2500k`), re-run `assemble_episode.py` and `deliver_episode.py`, then upload again.

## Files the operator gets

In Content Lab: the video, and the title, description and tags to copy. Also in the episode folder (and the fallback run artifact): `07_edit/redhat-engineer-<slug>-1080p.mp4`, `07_edit/captions.srt` (sidecar subtitles; the video also has captions burned in), `08_publish/thumbnail.png`, `08_publish/metadata.json`, `08_publish/delivery.json`, `08_publish/upload_log.json`. Content Lab has no thumbnail field, so the thumbnail is not uploaded.

## Limits

- The render is CRF 22 capped at `format.video_maxrate` (8M), which keeps a 6-minute file well under the upload limit (a measured 340 s episode is about 43 MB).
- Nothing is deleted after a run; a CI runner is discarded, and locally the operator clears old episode folders when they want the space.
- The operator posts, so there is no analytics feedback inside the cycle. Do not invent performance numbers.
