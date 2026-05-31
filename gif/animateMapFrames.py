#!/usr/bin/env python3
"""
Animate map frame PNGs into per-part GIFs using gifsicle.

Filename convention: {prefix}_frame-{N}_{PART}-{M}.png
Groups by PART-M, sorts frames by N, outputs one GIF per part.

Usage:
    python animateMapFrames.py <input_dir> [options]

Options:
    -o, --output DIR     Output directory (default: input_dir)
    -d, --delay INT      Frame delay in centiseconds (default: 100 = 1.0s)
    -l, --lossy INT      Gifsicle lossy level 0-200 (default: 30)
    --colors INT         Max colors 2-256 (default: 256)
    --disposal STR       GIF disposal method: background|previous|none (default: background)

Preprocessing (applied before GIF conversion — biggest levers for file size):
    --scale INT          Resize input to % of original, e.g. 50 = half size (default: 100)
    --max-width INT      Resize so width <= N px, preserving aspect ratio (overrides --scale)
    --dither STR         Dithering: FloydSteinberg|Riemersma|None (default: Riemersma)
                         None = smallest files, FloydSteinberg = smoothest gradients
"""

import argparse
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


FRAME_RE = re.compile(r"^(.+)_frame-(\d+)_(.+)\.png$", re.IGNORECASE)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input_dir", type=Path)
    p.add_argument("-o", "--output", type=Path, default=None)
    p.add_argument("-d", "--delay", type=int, default=100, help="centiseconds per frame (default: 100)")
    p.add_argument("-l", "--lossy", type=int, default=30, help="lossy compression 0-200 (default: 30)")
    p.add_argument("--colors", type=int, default=256, choices=range(2, 257), metavar="2-256")
    p.add_argument("--disposal", default="background", choices=["background", "previous", "none"])
    p.add_argument("--scale", type=int, default=100, metavar="1-100", help="resize input to %% of original (default: 100)")
    p.add_argument("--max-width", type=int, default=None, metavar="PX", help="resize so width <= PX, preserving aspect ratio")
    p.add_argument("--dither", default="Riemersma", choices=["FloydSteinberg", "Riemersma", "None"], help="dithering method (default: Riemersma)")
    return p.parse_args()


def check_deps():
    for tool, install in [("gifsicle", "brew install gifsicle"), ("convert", "brew install imagemagick")]:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except FileNotFoundError:
            sys.exit(f"{tool} not found — install with: {install}")


def group_frames(input_dir: Path) -> dict[str, list[tuple[int, Path]]]:
    groups: dict[str, list[tuple[int, Path]]] = defaultdict(list)
    for f in sorted(input_dir.glob("*.png")):
        m = FRAME_RE.match(f.name)
        if not m:
            print(f"  skip (no match): {f.name}")
            continue
        frame_num, part = int(m.group(2)), m.group(3)
        groups[part].append((frame_num, f))
    return groups


def png_to_gif(png: Path, tmp_dir: str, args) -> Path:
    out = Path(tmp_dir) / (png.stem + ".gif")

    resize_flag = None
    if args.max_width:
        resize_flag = f"{args.max_width}x10000>"  # constrain width, unlimited height
    elif args.scale != 100:
        resize_flag = f"{args.scale}%"

    cmd = ["convert", str(png)]
    if resize_flag:
        cmd += ["-resize", resize_flag]
    if args.dither == "None":
        cmd += ["+dither"]
    else:
        cmd += ["-dither", args.dither]
    cmd += ["-colors", str(args.colors), str(out)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"convert failed on {png.name}: {result.stderr.strip()}")
    return out


def animate(part: str, frames: list[tuple[int, Path]], output_dir: Path, args) -> None:
    frames_sorted = [path for _, path in sorted(frames, key=lambda x: x[0])]
    out_path = output_dir / f"{part}.gif"

    print(f"  {part}: {len(frames_sorted)} frames → {out_path.name}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_gifs = [png_to_gif(f, tmp_dir, args) for f in frames_sorted]

        cmd = [
            "gifsicle",
            f"--delay={args.delay}",
            "--loop",
            f"--colors={args.colors}",
            f"--disposal={args.disposal}",
            f"--lossy={args.lossy}",
            "--optimize=3",
            "--output", str(out_path),
        ] + [str(g) for g in temp_gifs]

        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  ERROR [{part}]: {result.stderr.strip()}", file=sys.stderr)
    else:
        size_kb = out_path.stat().st_size / 1024
        print(f"    done ({size_kb:.1f} KB)")


def main():
    args = parse_args()
    check_deps()

    if not args.input_dir.is_dir():
        sys.exit(f"Not a directory: {args.input_dir}")

    output_dir = args.output or args.input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    groups = group_frames(args.input_dir)
    if not groups:
        sys.exit("No matching PNG files found.")

    # Sort groups: by part name component (e.g. "OYO"), then numeric suffix (e.g. -1, -2)
    def part_sort_key(part: str):
        m = re.match(r"^(.*?)(\d+)$", part)
        if m:
            return (m.group(1), int(m.group(2)))
        return (part, 0)

    print(f"Found {len(groups)} part(s) in {args.input_dir}\n")
    for part in sorted(groups, key=part_sort_key):
        animate(part, groups[part], output_dir, args)

    print("\nDone.")


if __name__ == "__main__":
    main()
