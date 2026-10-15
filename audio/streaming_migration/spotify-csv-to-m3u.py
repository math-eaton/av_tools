# adapted from
# https://gist.github.com/lambdan/04e267266908bdc932912d69b9aac429

import os, json, csv, sys, re, subprocess, unicodedata
from tqdm import tqdm

# Export from Spotify using exportify.app, then run this on it when you have the songs!

metaFile = "meta.json"
audioExts = [".mp3", ".flac", ".ogg", ".opus", ".wav", ".m4a", ".aac"]
musicDir = "/mnt/media/data/music/"
# Playlists are written inside musicDir so Navidrome (which only mounts
# musicDir, not its parent) can see and scan them.
playlistsDir = os.path.join(musicDir, "Playlists")

if len(sys.argv) < 2:
    print("Usage: python csv-to-m3u.py <csv_file>")
    print("Example: python csv-to-m3u.py my_playlist.csv")
    sys.exit(1)

csvFile = sys.argv[1]
if not os.path.exists(csvFile):
    print(f"CSV file {csvFile} does not exist.")
    sys.exit(1)

def getMeta(filepath):
    try:
        fullpath = os.path.abspath(filepath)
        if not os.path.exists(fullpath):
            print(f"File {fullpath} no longer exists, skipping.")
            return None
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", fullpath]
        called = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        jsonData = json.loads(called.stdout)
        isrc = jsonData.get("format", {}).get("tags", {}).get("ISRC", "")
        return {
            "ext": os.path.splitext(filepath)[1].lower().strip().removeprefix("."),
            "isrc": isrc.strip() if isrc else None,
            "ffprobe": jsonData
        }
    except Exception as e:
        print(f"Error extracting ISRC from {filepath}: {e}")
    return None

def save(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Saved")


seen = set()
metaDict = {}
if os.path.isfile(metaFile):
    with open(metaFile, 'r', encoding='utf-8') as f:
        metaDict = json.load(f)
seen = set(metaDict.keys())

def buildDict():
    for root, dirs, files in tqdm(os.walk(musicDir)):
        needToSave = False
        for file in tqdm(files):
            if any(file.lower().endswith(ext) for ext in audioExts):
                filepath = os.path.join(root, file)
                if filepath in seen:
                    continue
                meta = getMeta(filepath)
                if meta is not None:
                    metaDict[filepath] = meta
                seen.add(filepath)
                needToSave = True
        if needToSave:
            save(metaDict, metaFile)

# go through folder and build ISRC/tag dict
buildDict()

# check for missing files
needToSave = False
for filepath in tqdm(list(metaDict.keys())):
    if not os.path.exists(filepath):
        print(f"File {filepath} does not exist, removing from metaDict")
        del metaDict[filepath]
        seen.discard(filepath)
        needToSave = True
if needToSave:
    save(metaDict, metaFile)

def normalize(s):
    """Lowercase, strip accents/punctuation, collapse whitespace for fuzzy matching."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()

def getTag(tags, *names):
    if not tags:
        return ""
    lower = {k.lower(): v for k, v in tags.items()}
    for name in names:
        v = lower.get(name.lower())
        if v:
            return v.strip()
    return ""

# Build lookup indexes once, instead of rescanning metaDict per CSV row.
isrcIndex = {}
fallbackIndex = {}
for filepath, meta in metaDict.items():
    fp_isrc = (meta.get("isrc") or "").strip().upper()
    if fp_isrc:
        isrcIndex.setdefault(fp_isrc, []).append(filepath)

    tags = meta.get("ffprobe", {}).get("format", {}).get("tags", {})
    file_title = getTag(tags, "title")
    file_artist = getTag(tags, "artist", "album_artist")
    if file_title and file_artist:
        fb_key = (normalize(file_artist), normalize(file_title))
        fallbackIndex.setdefault(fb_key, []).append(filepath)

def pickBest(filepaths):
    """Prefer FLAC among candidates, otherwise take the first."""
    best = filepaths[0]
    for fp in filepaths[1:]:
        if metaDict[fp].get("ext") == "flac" and metaDict[best].get("ext") != "flac":
            best = fp
    return best

final = {}
missing = []
with open(csvFile, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f) # type: ignore
    data = [row for row in reader]
    print(len(data), "rows found in CSV")
    for d in data:
        title = d.get("Track Name", "")
        artist = d.get("Artist Name(s)", "")
        album = d.get("Album Name", "")
        album_artist = d.get("Album Artist Name(s)", "")
        isrc = d.get("ISRC", "")
        key = isrc if isrc else f"{artist} - {title} - {album}"

        candidates = isrcIndex.get(isrc.strip().upper(), []) if isrc else []
        matched_by = "isrc" if candidates else None
        if not candidates:
            candidates = fallbackIndex.get((normalize(artist), normalize(title)), [])
            matched_by = "title/artist" if candidates else None

        if candidates:
            filepath = pickBest(candidates)
            if key in final and final[key]["ext"] == "flac":
                continue  # prefer FLAC if already matched
            final[key] = {
                "filepath": filepath,
                "title": title,
                "artist": artist,
                "album": album,
                "album_artist": album_artist,
                "isrc": isrc,
                "ext": metaDict[filepath].get("ext", ""),
                "matched_by": matched_by,
            }
        else:
            print("Missing", isrc, title, artist, album, album_artist)
            missing.append({
                "title": title,
                "artist": artist,
                "album": album,
                "album_artist": album_artist,
                "isrc": isrc
            })

print("Got", len(final), "tracks matched;", len(missing), "missing")

os.makedirs(playlistsDir, exist_ok=True)
csvBasename = os.path.splitext(os.path.basename(csvFile))[0]

out = "#EXTM3U\n"
for track in final.values():
    relpath = os.path.relpath(track["filepath"], playlistsDir)
    out += f"#EXTINF:-1,{track['artist']} - {track['title']}\n"
    out += f"{relpath}\n"

outputFile = os.path.join(playlistsDir, csvBasename + ".m3u")
with open(outputFile, 'w', encoding='utf-8') as f:
    f.write(out)
print(f"Playlist written to {outputFile}")

if missing:
    missingFile = os.path.join(os.path.dirname(os.path.abspath(csvFile)), csvBasename + "_missing.csv")
    with open(missingFile, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["artist", "album", "album_artist", "title", "isrc"])
        writer.writeheader()
        writer.writerows(missing)
    print(f"Missing-track reference written to {missingFile}")
