# Publishing, scheduling and verification

`scripts/publish.py` is the CEO's signing hand. It talks to Amplifier for auth and
registration, and to YouTube for the actual upload. It never produces or edits the
video.

## 1. The flow

```
local master
   │
   ├─ validate title / description / tags / privacy
   ├─ Amplifier: mint a 1-hour YouTube access token for the target channel
   ├─ YouTube: resumable videos.insert (snippet + status)
   ├─ YouTube: thumbnails.set
   ├─ Amplifier: POST /api/publications/register  (so analytics can find it)
   └─ verify: URL, privacy, thumbnail, publication status
```

The refresh token stays on the Amplifier server. The agent only ever sees a
short-lived access token.

## 2. Commands

```bash
SKILL_DIR="$HOME/.claude/skills/amplifier-yt-skill"
PUB="$SKILL_DIR/scripts/publish.py"

# who is connected
python3 "$PUB" channels

# mint a token (debugging; prints a secret, do not paste it into chat)
python3 "$PUB" token --channel "Business Mafia"

# private draft for review (default privacy)
python3 "$PUB" upload \
  --video final/episode.mp4 \
  --channel "Business Mafia" \
  --title "ढाबा वाला कितना कमाता है?" \
  --description-file final/description.txt \
  --tags "business,hindi,dhaba" \
  --thumbnail final/thumbnail.jpg \
  --privacy private

# unlisted review link
python3 "$PUB" upload ... --privacy unlisted

# public release (explicit yes required)
python3 "$PUB" upload ... --privacy public --yes

# scheduled public release (stays private until the time)
python3 "$PUB" upload ... --publish-at 2026-10-30T18:00:00+05:30 --yes

# edit packaging on an existing video
python3 "$PUB" update \
  --channel "RedHat Engineer" \
  --video-id dQw4w9WgXcQ \
  --title "The Clock That Made Time Public" \
  --thumbnail final/thumb2.jpg

# register a video uploaded outside this skill
python3 "$PUB" register \
  --channel "Wild Thinking" \
  --youtube-video-id dQw4w9WgXcQ \
  --title "..." --description "..."

# poll an Amplifier publication
python3 "$PUB" status --video-id <amplifierVideoId> --wait 300
```

`--dry-run` mints a token, validates metadata and prints what would happen. It
does not upload. Use it on every new channel and every public release.

## 3. Privacy rules

- Default is **private**. That is deliberate.
- **Unlisted** is the review state: the owner can watch without it going public.
- **Public** requires `--yes`. Do not pass `--yes` unless the owner explicitly
  approved this exact video in this conversation.
- **Scheduled** is `--publish-at` with private privacy. YouTube flips it public at
  the timestamp. The timestamp must include a timezone (`+05:30`, `Z`).
- Multi-channel uploads require `--yes`. The same video on several channels is
  duplicate content; only do it when the owner deliberately wants a fan-out.
- Never change a live video to public as a "test". Use unlisted.

## 4. Metadata limits

| Field | Limit | Notes |
|---|---|---|
| Title | 100 chars | Mobile truncates around 70; aim for 55–65 |
| Description | 5,000 chars | First 150 chars are the search snippet |
| Tags | 500 chars total | Comma-separated; no `#` needed |
| Thumbnail | 2 MB, 1280×720, JPG/PNG | 16:9; text must survive phone size |
| Category | YouTube category id | Default 22 (People & Blogs) |
| Publish time | ISO 8601 + timezone | Must be in the future |

The script validates title length, angle brackets, description length, tag length,
privacy and publish time before it touches YouTube.

## 5. Scheduling

- `--publish-at 2026-10-30T18:00:00+05:30` sends `status.publishAt` and
  `privacyStatus=private`.
- YouTube requires the video to be private when `publishAt` is set.
- The schedule is a promise to the audience, not a suggestion. Put it on the slate
  with `slate-status --status scheduled`.
- If the video is not ready, move the slate date; do not upload a placeholder.

## 6. Editing an existing video

`publish.py update` fetches the current `snippet` and `status`, merges only the
fields you pass, and sends a replace-style update. This avoids the classic mistake
of clearing the description or tags by sending a partial snippet.

- `--title` and `--description`/`--description-file` update the snippet.
- `--tags` replaces the tag list.
- `--privacy` changes visibility; `public` needs `--yes`.
- `--thumbnail` sets a new thumbnail.
- `--publish-at` reschedules; it forces private until the time.

Updating YouTube metadata does **not** update Amplifier's stored metadata. That is
fine for analytics, but if the title change matters to the ledger, note it in the
decision log.

## 7. Registration and analytics

After a direct upload, the script calls:

```
POST /api/publications/register
{ "channelId": "<amplifier channel id>",
  "youtubeVideoId": "...",
  "metadata": { "title", "description", "tags", "privacy" } }
```

This creates the Publication row that `/api/analytics/videos/:videoId` uses. If
registration fails, the video is live but invisible to Amplifier analytics. Fix it
with:

```bash
python3 "$PUB" register --channel "..." --youtube-video-id "..." --title "..."
```

Do not leave an orphan upload.

## 8. Verification checklist

After every upload:

- [ ] `youtubeUrl` opens and the video plays.
- [ ] Privacy is what you intended (`private`, `unlisted`, `public`).
- [ ] The thumbnail is the one you approved, not a random frame.
- [ ] The title and description are not truncated or mangled (Devanagari, emoji).
- [ ] Chapters in the description start at `0:00` and are at least 10 seconds apart.
- [ ] The video is on the correct channel (check the channel name in the URL/page).
- [ ] The Amplifier publication is registered and eventually `succeeded`.
- [ ] The slate row is `scheduled` or `published`.

## 9. Failure modes

| Error | Likely cause | Fix |
|---|---|---|
| `invalid_grant` | refresh token revoked/expired | reconnect the channel in Amplifier |
| 401/403 on upload | token expired mid-upload or missing scope | re-mint the token, retry |
| `quotaExceeded` | daily YouTube API quota | wait for the reset; do not retry in a loop |
| `uploadLimitExceeded` | channel's daily upload limit | wait; schedule tomorrow |
| thumbnail 403 | channel not verified for custom thumbnails | verify the channel, or ship without |
| `publishAt` rejected | privacy not private, or timezone missing | use `--publish-at` with `+05:30` and private |
| 400 on title | `<` or `>` in the title, or >100 chars | rewrite the title |
| 400 on tags | total tag length >500 | trim the list |
| upload stalls | large file / flaky network | resumable upload retries; try a smaller master |
| registration failed | Amplifier API/key issue | fix and `publish.py register` |

## 10. Security

- The agent key (`amp_...`) is a bearer secret. Keep it in
  `~/.config/amplifier/agent_key` or an env var, never in a repo or a chat message.
- The minted YouTube access token lasts about an hour. Do not log it, paste it, or
  store it in the ledger.
- Revoke a leaked agent key in the Amplifier UI (`DELETE /api/auth/agent-key/:id`).
- Do not use a personal Google account token directly; always go through Amplifier
  so the refresh token stays server-side.

## 11. What this script deliberately does not do

- It does not delete videos or channels.
- It does not change channel branding, playlists or comments.
- It does not buy ads or change monetisation.
- It does not publish public without `--yes`.
- It does not upload to a channel that is not connected in Amplifier.

If the owner asks for one of those, say what is missing and do it in the YouTube
UI with them, not by improvising an API call.
