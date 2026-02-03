#!/bin/zsh

# Download from web in native resolution/audio
# Usage: ./yt-dlp.zsh [URL]

URL="${1:-xyz}"

# Using android_creator and web clients to avoid 403 errors

/usr/local/bin/yt-dlp \
  --extractor-args "youtube:player_client=android_creator,web;player_skip=configs" \
  --format "bestvideo+bestaudio/best" \
  --merge-output-format mkv \
  --output "%(title)s.%(ext)s" \
  "$URL"