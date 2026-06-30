#!/bin/sh

# Download from web in native resolution/audio
# Usage: ./yt-dlp.sh [URL]


URL="${1:-${YTDLP_DEFAULT_URL:-}}"
YTDLP="${YTDLP_BIN:-yt-dlp}"

# Using android_creator and web clients to avoid 403 errors

"$YTDLP" \
  --extractor-args "youtube:player_client=android_creator,web;player_skip=configs" \
  --format "bestvideo+bestaudio/best" \
  --merge-output-format mkv \
  --output "%(title)s.%(ext)s" \
  "$URL"
