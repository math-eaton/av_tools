import argparse
import collections
import itertools
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")


def normalize_mode(img):
    """Return img as RGB or RGBA (8-bit), regardless of source mode/colorspace."""
    mode = img.mode
    if mode in ("RGB", "RGBA"):
        return img
    if mode == "P":
        return img.convert("RGBA") if "transparency" in img.info else img.convert("RGB")
    if mode in ("L", "1"):
        return img.convert("RGB")
    if mode == "LA":
        return img.convert("RGBA")
    if mode == "CMYK":
        return img.convert("RGB")
    if mode.startswith("I") or mode == "F":
        # 16/32-bit integer or float grayscale: values aren't 0-255, so convert()
        # would just clip/garble them. Rescale into 8-bit range first.
        arr = np.asarray(img, dtype=np.float64)
        arr -= arr.min()
        peak = arr.max()
        if peak > 0:
            arr = arr / peak * 255.0
        return Image.fromarray(arr.astype(np.uint8), mode="L").convert("RGB")
    # Anything else (e.g. YCbCr): best-effort fallback.
    return img.convert("RGBA")


def load_frame(path, alpha_color, target_size):
    with Image.open(path) as img:
        img = normalize_mode(img)
        if img.size != target_size:
            img = img.resize(target_size, Image.LANCZOS)

        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, alpha_color)
            bg.paste(img, mask=img.getchannel("A"))
            arr = np.asarray(bg)
        else:
            arr = np.asarray(img)

        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def even_size(size):
    # yuv420p (required for broad H.264 compatibility) needs even width/height.
    w, h = size
    return (w + (w % 2), h + (h % 2))


def iter_frames(image_files, alpha_color, target_size, workers, prefetch=None):
    """Decode frames on a bounded thread-pool pipeline so disk I/O and PNG
    decode overlap with video writing, without buffering unbounded memory."""
    if prefetch is None:
        prefetch = workers * 4

    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = collections.deque()
        files_iter = iter(image_files)

        for path in itertools.islice(files_iter, prefetch):
            pending.append(executor.submit(load_frame, path, alpha_color, target_size))

        for path in files_iter:
            pending.append(executor.submit(load_frame, path, alpha_color, target_size))
            yield pending.popleft().result()

        while pending:
            yield pending.popleft().result()


def read_manifest(manifest_path, base_dir=None):
    """Read a line-delimited list of image paths giving explicit frame order.
    Blank lines and lines starting with '#' are skipped. Relative paths are
    resolved against base_dir (if given)."""
    paths = []
    with open(manifest_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if base_dir and not os.path.isabs(line):
                line = os.path.join(base_dir, line)
            paths.append(line)

    if not paths:
        raise SystemExit(f"Manifest '{manifest_path}' contains no image paths.")

    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        preview = "\n".join(missing[:10])
        more = f"\n...and {len(missing) - 10} more" if len(missing) > 10 else ""
        raise SystemExit(f"Manifest '{manifest_path}' references {len(missing)} missing file(s):\n{preview}{more}")

    return paths


def create_video(image_files, video_path, fps, alpha_color=(255, 255, 255), workers=8, crf=20):
    if not image_files:
        raise ValueError("No input images found to assemble into a video.")

    with Image.open(image_files[0]) as first:
        source_size = normalize_mode(first).size
    target_size = even_size(source_size)
    width, height = target_size

    # Pipe decoded frames straight into a single libx264 encode instead of
    # writing a lossy OpenCV intermediate and re-encoding it with ffmpeg
    # afterwards -- that two-pass approach roughly doubles total encode time
    # and disk I/O for large (10k+ frame) runs with no quality benefit, since
    # the OpenCV pass is thrown away immediately after.
    command = [
        "ffmpeg", "-y", "-loglevel", "warning",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{width}x{height}", "-r", str(fps),
        "-i", "-",
        "-vcodec", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
        video_path,
    ]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)

    total = len(image_files)
    start = time.monotonic()
    try:
        for i, frame in enumerate(iter_frames(image_files, alpha_color, target_size, workers), 1):
            proc.stdin.write(frame.tobytes())
            if i % 500 == 0 or i == total:
                elapsed = time.monotonic() - start
                rate = i / elapsed if elapsed > 0 else 0.0
                print(f"  encoded {i}/{total} frames ({rate:.1f} fps)", flush=True)
    finally:
        proc.stdin.close()
        proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode} while encoding '{video_path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image to Video Conversion Script")
    parser.add_argument("--input_dir", help="Input directory containing image files (required unless --manifest is given)")
    parser.add_argument("--manifest", help="Optional text file listing image paths in desired frame order, one per line (overrides alphabetical directory ordering); relative paths are resolved against --input_dir")
    parser.add_argument("--output_dir", required=True, help="Output directory for the video file")
    parser.add_argument("--output_video_name", required=True, help="Name of the output video file")
    parser.add_argument("--framerate", type=float, default=13.0, help="Framerate for the output video (default: 13.0)")
    parser.add_argument("--alpha_color", nargs=3, type=int, default=[255, 255, 255], help="Alpha color as RGB values (default: 255 255 255)")
    parser.add_argument("--crf", type=int, default=20, help="Constant Rate Factor (CRF) for video encoding (default: 20)")
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 4), help="Thread-pool size for decoding frames (default: min(8, cpu_count))")
    args = parser.parse_args()

    alpha_color = tuple(args.alpha_color)

    if args.manifest:
        image_files = read_manifest(args.manifest, base_dir=args.input_dir)
    else:
        if not args.input_dir:
            raise SystemExit("--input_dir is required when --manifest is not provided.")
        image_folder = args.input_dir
        image_files = sorted(
            os.path.join(image_folder, img)
            for img in os.listdir(image_folder)
            if img.lower().endswith(IMAGE_EXTENSIONS)
        )
        if not image_files:
            raise SystemExit(f"No images with extensions {IMAGE_EXTENSIONS} found in '{image_folder}'.")

    os.makedirs(args.output_dir, exist_ok=True)

    output_video_name = args.output_video_name
    if not output_video_name.lower().endswith(".mp4"):
        output_video_name += ".mp4"
    output_video_path = os.path.join(args.output_dir, output_video_name)

    create_video(
        image_files,
        output_video_path,
        args.framerate,
        alpha_color=alpha_color,
        workers=args.workers,
        crf=args.crf,
    )

    print("video complete:", output_video_path)
