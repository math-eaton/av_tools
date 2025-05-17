#!/usr/bin/env python3
import sys

# Album/disc metadata
album_title = "Shadowboxing"
album_performer = "Docents"
disc_id = "TT13"

# Track metadata list: each track has file path, title, and ISRC code.
tracks = [
    {"file": "audio/burn_cd/data/1_docents_garden_IJMaster.wav",         "title": "Garden",        "isrc": "QZNWZ2598247"},
    {"file": "audio/burn_cd/data/2_docents_shadowboxing_IJMaster.wav",   "title": "Shadowboxing",  "isrc": "QZNWZ2598248"},
    {"file": "audio/burn_cd/data/3_docents_double-Fantasy_IJMasterRecall.wav", "title": "Double Fantasy", "isrc": "QZNWZ2598249"},
    {"file": "audio/burn_cd/data/4_docents_shouldnt-We_IJMasterRecall.wav", "title": "Shouldn't We",   "isrc": "QZNWZ2598250"},
    {"file": "audio/burn_cd/data/5_docents_workout_IJMaster-mjhgap.wav", "title": "Workout",       "isrc": "QZNWZ2598251"}
]

# Function to escape special characters in text fields for the CUE sheet
def escape_text(text):
    # Replace double quotes with two single quotes to avoid breaking .cue syntax
    text = text.replace('"', "''")
    # (Apostrophes and other punctuation are safe within double quotes)
    return text

# Determine output cue sheet filename (e.g., use album title or disc ID)
cue_filename = f"{album_title}.cue"
# If needed, you could use disc_id for the filename instead:
# cue_filename = f"{disc_id}.cue"

# Open the output .cue file for writing
with open(cue_filename, "w", encoding="utf-8") as cue_file:
    # Write disc-level CD-Text metadata
    cue_file.write(f'TITLE "{escape_text(album_title)}"\n')
    cue_file.write(f'PERFORMER "{escape_text(album_performer)}"\n')
    # If a numeric UPC/EAN code is available, use the CATALOG command (13-digit number)
    # e.g., cue_file.write(f'CATALOG "0123456789123"\n')
    # Here, we use a REM comment to include the disc ID since it's not a standard UPC/EAN
    cue_file.write(f'REM COMMENT "Disc ID: {disc_id}"\n')
    cue_file.write("\n")  # blank line separator

    # Write track-level metadata for each track
    for idx, track in enumerate(tracks, start=1):
        file_path = track["file"]
        track_title = track["title"]
        track_isrc = track.get("isrc", "")
        # Use track-specific performer if provided, otherwise default to album performer
        track_performer = track.get("performer", album_performer)
        # Write file reference and track details
        cue_file.write(f'FILE "{file_path}" WAVE\n')
        cue_file.write(f'  TRACK {idx:02d} AUDIO\n')
        cue_file.write(f'    TITLE "{escape_text(track_title)}"\n')
        cue_file.write(f'    PERFORMER "{escape_text(track_performer)}"\n')
        if track_isrc:
            cue_file.write(f'    ISRC {track_isrc}\n')
        # Track index (start of track in the file)
        cue_file.write('    INDEX 01 00:00:00\n')

# Optionally print instructions for burning the CD using cdrdao or cdrecord
print_instructions = True
if len(sys.argv) > 1 and sys.argv[1].lower() in ("--no-instructions", "--noinstr", "--no-print"):
    print_instructions = False

if print_instructions:
    print(f'CUE sheet generated: "{cue_filename}"')
    print("To burn the audio CD with cdrdao (with CD-Text metadata):")
    print(f'  cdrdao write --device <YOUR-CD-DEVICE> --driver generic-mmc:0x10 "{cue_filename}"')
    print("Alternatively, to burn with cdrecord (cdrtools) using the CUE sheet:")
    print(f'  cdrecord -v dev=<YOUR-CD-DEVICE> -dao -text cuefile="{cue_filename}"')
