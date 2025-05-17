#!/bin/bash
# requires imagemagick

# Check if input is provided
if [ -z "$1" ]; then
  echo "Usage: $0 input.psd"
  exit 1
fi

INPUT="$1"
OUTPUT="${INPUT%.*}.png"

# Convert PSD to PNG - layers are exported as separate images
magick "$INPUT" "$OUTPUT"

echo "Exported $OUTPUT"