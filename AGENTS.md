# Amplifier — Secrets & API Reference

> Repo-level agent instructions. The reference below is kept in a fenced block so
> the `#` comment lines render literally. Placeholders only — no live tokens.

```text
# =============================================================================
# Amplifier / YouTube upload — secrets & API reference for GitHub Secrets
# =============================================================================
# HOW TO USE:
#   1. Copy each KEY=VALUE pair below into GitHub:
#        Repo -> Settings -> Secrets and variables -> Actions -> New repository secret
#   2. Fill in the real AMPLIFIER_API_KEY value yourself (from
#        ~/.config/amplifier/agent_key on the machine that runs publish.py).
#      NEVER commit the real key to this repo, a workflow file, or a chat.
#
# NOTE: GitHub Actions accepts one KEY=VALUE per secret, no comments.
#       Only the block in section 1 is meant for GitHub Secrets.
#       This file contains PLACEHOLDERS only — no live tokens.
# =============================================================================


# -----------------------------------------------------------------------------
# 1. GITHUB SECRETS (add each of these as a separate repository secret)
# -----------------------------------------------------------------------------

ALREADY ADDED INTO THE SECRETS

# -----------------------------------------------------------------------------
# 2. SECRETS THAT EXIST, BUT ARE *NOT* STORED HERE (by design)
# -----------------------------------------------------------------------------
# - YouTube refresh token  : lives ONLY on the Amplifier server. The agent never
#                            sees it; /api/channels/{id}/token mints a 1-hour
#                            access token per upload.
# - YouTube access token   : ephemeral (~1 hour), minted at upload time. Never
#                            stored, logged, or committed.
# - Google OAuth client ID/secret : not needed locally; OAuth runs inside
#                            Amplifier.
#
# If the agent key ever leaks, revoke it in the Amplifier UI:
#   DELETE /api/auth/agent-key/:id


# -----------------------------------------------------------------------------
# 3. API ENDPOINTS USED BY THE UPLOAD PIPELINE (reference, not secrets)
# -----------------------------------------------------------------------------

# --- Amplifier API (auth: Bearer $AMPLIFIER_API_KEY) ---
# GET    /api/health                                  health check (doctor)
# GET    /api/channels                                list connected channels
# GET    /api/channels/{id}/token                     mint 1h YouTube access token
# POST   /api/publications/register                   register upload for analytics
# GET    /api/publications?videoId=...                poll publication status
# GET    /api/analytics/overview?range=...            portfolio analytics
# GET    /api/analytics/videos/{videoId}?range=...    per-video analytics
# GET    /api/analytics/channels/{id}?range=...       per-channel analytics
# DELETE /api/auth/agent-key/:id                      revoke a leaked key (Amplifier UI)

# --- YouTube Data API v3 (auth: Bearer minted access token) ---
# POST   https://www.googleapis.com/upload/youtube/v3/videos               resumable videos.insert (upload)
# POST   https://www.googleapis.com/upload/youtube/v3/thumbnails/set       set custom thumbnail
# GET    https://www.googleapis.com/youtube/v3/videos                      fetch current metadata (update)
# PUT    https://www.googleapis.com/youtube/v3/videos                      replace-style metadata update

# --- YouTube Analytics API v2 (used by ceo.py sync, if enabled) ---
# GET    https://youtubeanalytics.googleapis.com/v2/reports


# -----------------------------------------------------------------------------
# 4. QUICK WORKFLOW EXAMPLE (.github/workflows/upload.yml)
# -----------------------------------------------------------------------------
# name: Upload video
# on: workflow_dispatch
# jobs:
#   upload:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#         with: { python-version: "3.11" }
#       - run: pip install requests
#       - name: Upload (private by default)
#         env:
#           AMPLIFIER_API_KEY: ${{ secrets.AMPLIFIER_API_KEY }}
#           AMPLIFIER_API_URL: ${{ secrets.AMPLIFIER_API_URL }}
#         run: |
#           python3 "$HOME/.claude/skills/amplifier-yt-skill/scripts/publish.py" upload \
#             --video final/episode.mp4 \
#             --channel "Business Mafia" \
#             --title "..." \
#             --description-file final/description.txt \
#             --tags "..." \
#             --thumbnail final/thumbnail.jpg \
#             --privacy private
```
