#!/usr/bin/env python3
"""Recursively split monolithic FLAC/APE albums into per-track FLACs via their cue sheets.

For every .cue file found under the given root:
  - locate the monolithic audio file it references (.flac or .ape)
  - skip it if that source file is missing (nothing to split, or already split)
  - skip it if the album already has as many standalone track FLACs as the
    cue declares (already extracted)
  - convert .ape sources to .flac with ffmpeg first, then split with shnsplit
  - tag the resulting tracks from the cue sheet with cuetag

Requires: shnsplit, ffmpeg, cuetag (all from cuetools/flac/ffmpeg packages).
"""

import argparse
import contextlib
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

FILE_LINE_RE = re.compile(r'^\s*FILE\s+"(?P<name>.+)"\s+\S+\s*$', re.IGNORECASE)
TRACK_LINE_RE = re.compile(r'^\s*TRACK\s+\d+\s+AUDIO\s*$', re.IGNORECASE)


def read_cue(cue_path: Path):
    """Return (text, encoding_used). Falls back through common cue encodings,
    since many cue sheets (esp. older/non-English ones) aren't UTF-8."""
    raw = cue_path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace"), "latin-1"


def parse_cue_text(text: str):
    """Return (referenced_file_name_or_None, track_count)."""
    file_name = None
    track_count = 0
    for line in text.splitlines():
        if file_name is None:
            m = FILE_LINE_RE.match(line)
            if m:
                file_name = m.group("name")
        if TRACK_LINE_RE.match(line):
            track_count += 1
    return file_name, track_count


@contextlib.contextmanager
def cue_for_tools(cue_path: Path, text: str, encoding: str, dry_run: bool):
    """Yield a cue file path that is guaranteed UTF-8.

    shnsplit/cuetag copy the cue's TITLE/PERFORMER bytes verbatim into output
    filenames and tags. If the source cue is cp1252/latin-1 (common for older
    or non-English releases), that produces filenames with invalid UTF-8
    bytes on disk. Re-encoding to a UTF-8 temp copy fixes it at the source.
    """
    if dry_run or encoding in ("utf-8", "utf-8-sig"):
        yield cue_path
        return
    with tempfile.TemporaryDirectory(prefix="extractFLAC_cue_") as tmpdir:
        normalized = Path(tmpdir) / cue_path.name
        normalized.write_text(text, encoding="utf-8")
        yield normalized


def resolve_source(cue_path: Path, referenced_name: str | None) -> Path | None:
    directory = cue_path.parent
    candidates = []
    if referenced_name:
        candidates.append(directory / referenced_name)
    candidates.append(directory / f"{cue_path.stem}.flac")
    candidates.append(directory / f"{cue_path.stem}.ape")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    if referenced_name:
        target = referenced_name.lower()
        for f in directory.iterdir():
            if f.is_file() and f.name.lower() == target:
                return f
    return None


def already_split(directory: Path, source: Path, track_count: int) -> bool:
    if track_count <= 0:
        return False
    existing = [f for f in directory.glob("*.flac") if f.resolve() != source.resolve()]
    return len(existing) >= track_count


def run(cmd, cwd=None, dry_run=False, verbose=False):
    if verbose or dry_run:
        prefix = "  [dry-run] $ " if dry_run else "  $ "
        print(prefix + " ".join(shlex.quote(c) for c in cmd))
    if dry_run:
        return
    subprocess.run(cmd, cwd=cwd, check=True)


def convert_ape_to_flac(ape_path: Path, dry_run: bool, verbose: bool) -> Path:
    flac_path = ape_path.with_suffix(".flac")
    if flac_path.exists():
        print(f"  Converted FLAC already exists, reusing: {flac_path.name}")
        return flac_path
    print(f"  Converting APE -> FLAC: {ape_path.name}")
    run(["ffmpeg", "-n", "-loglevel", "error", "-i", str(ape_path), str(flac_path)],
        dry_run=dry_run, verbose=verbose)
    return flac_path


def split_album(directory: Path, tool_cue: Path, source: Path, tag: bool, dry_run: bool, verbose: bool):
    run(["shnsplit", "-f", str(tool_cue), "-o", "flac", "-t", "%n-%t", str(source)],
        cwd=directory, dry_run=dry_run, verbose=verbose)

    if not tag or dry_run:
        return
    split_files = sorted(directory.glob("[0-9][0-9]-*.flac"))
    if split_files:
        run(["cuetag", str(tool_cue), *[str(f) for f in split_files]],
            dry_run=dry_run, verbose=verbose)
    else:
        print("  Warning: no split track files matched '[0-9][0-9]-*.flac', skipping cuetag")


def find_cue_files(root: Path):
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() == ".cue")


def process_cue(cue_path: Path, tag: bool, dry_run: bool, verbose: bool) -> str:
    rel = cue_path
    text, encoding = read_cue(cue_path)
    referenced_name, track_count = parse_cue_text(text)

    if track_count == 0:
        print(f"[skip] {rel}: no TRACK entries parsed from cue")
        return "skip"

    source = resolve_source(cue_path, referenced_name)
    if source is None:
        print(f"[skip] {rel}: no monolithic source file found (already split, or missing)")
        return "skip"

    if already_split(cue_path.parent, source, track_count):
        print(f"[skip] {rel}: already split ({track_count} tracks present)")
        return "skip"

    print(f"[split] {rel} <- {source.name} ({track_count} tracks)")
    if encoding not in ("utf-8", "utf-8-sig"):
        print(f"  Note: cue sheet decoded as {encoding}, not UTF-8; normalizing a copy "
              f"for shnsplit/cuetag so output filenames/tags come out valid UTF-8")
    try:
        if source.suffix.lower() == ".ape":
            flac_source = convert_ape_to_flac(source, dry_run, verbose)
        else:
            flac_source = source
        with cue_for_tools(cue_path, text, encoding, dry_run) as tool_cue:
            split_album(cue_path.parent, tool_cue, flac_source, tag, dry_run, verbose)
    except subprocess.CalledProcessError as exc:
        print(f"[error] {rel}: command failed ({exc})", file=sys.stderr)
        return "error"
    return "split"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=".", help="Root directory to search recursively (default: cwd)")
    parser.add_argument("--no-tag", action="store_true", help="Skip cuetag metadata tagging after splitting")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without running anything")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print commands as they are run")
    args = parser.parse_args()

    # Filenames elsewhere in the library may carry non-UTF-8 bytes (surrogate-escaped
    # by the OS). Don't let printing one crash the whole batch.
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.stderr.reconfigure(errors="backslashreplace")

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    cue_files = find_cue_files(root)
    if not cue_files:
        print(f"No .cue files found under {root}")
        return

    counts = {"split": 0, "skip": 0, "error": 0}
    for cue_path in cue_files:
        result = process_cue(cue_path, tag=not args.no_tag, dry_run=args.dry_run, verbose=args.verbose)
        counts[result] += 1

    print(f"\nDone: {counts['split']} split, {counts['skip']} skipped, {counts['error']} errors "
          f"(out of {len(cue_files)} cue sheets found)")
    if counts["error"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
