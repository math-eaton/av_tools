#!/bin/zsh

# Download from client in native resolution/audio
# Usage: ./yt-dlp.zsh

URL="xyz"

# Use Homebrew yt-dlp (latest version)
/usr/local/bin/yt-dlp \
  --format "bestvideo+bestaudio/best" \
  --merge-output-format mkv \
  --output "%(title)s.%(ext)s" \
  --verbose \
  "$URL"