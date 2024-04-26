import os
import subprocess
from PIL import Image, UnidentifiedImageError, ImageStat
import numpy as np
from tqdm import tqdm
import argparse

def is_frame_corrupt(frame_path):
    try:
        with Image.open(frame_path) as img:
            img.verify()  # Verify the image integrity
        return False
    except (IOError, UnidentifiedImageError):
        return True

def count_dark_pixels(image, threshold=50):
    grayscale = image.convert('L')
    np_image = np.array(grayscale)
    return np.sum(np_image < threshold)

def remove_outlier_frames(frame_paths, resize, z_threshold=2):
    frames = [Image.open(f).convert('RGBA').resize(resize, Image.NEAREST) for f in frame_paths]
    dark_counts = [count_dark_pixels(frame) for frame in frames]

    median_dark = np.median(dark_counts)
    std_dark = np.std(dark_counts)

    valid_frames = [frame for frame, count in zip(frames, dark_counts) if abs(count - median_dark) <= z_threshold * std_dark]
    return valid_frames



def convert_video_to_gif(input_video, output_gif, resize=(1024, 768), frame_rate=12):
    # Create a temporary directory for frames
    temp_dir = "temp_frames"
    os.makedirs(temp_dir, exist_ok=True)

    # Check if the input video file exists
    if not os.path.isfile(input_video):
        print(f"Input video file '{input_video}' does not exist.")
        return

    # Determine the input video file extension
    _, input_extension = os.path.splitext(input_video)
    input_extension = input_extension.lower()

    # Choose the appropriate FFmpeg codec based on the input file extension
    if input_extension == ".mov":
        codec = "png"
    elif input_extension == ".mp4":
        codec = "libx264"
    else:
        print(f"Unsupported input video format: {input_extension}")
        return

    # Convert the video to individual frames using FFmpeg
    subprocess.call([
        'ffmpeg',
        '-i', input_video,
        '-r', str(frame_rate),  # Frame rate
        os.path.join(temp_dir, 'frame%04d.png')
    ])

    # Read all the frames and filter out corrupt ones
    frame_files = sorted(os.path.join(temp_dir, f) for f in os.listdir(temp_dir))
    non_corrupt_frames = [f for f in frame_files if not is_frame_corrupt(f)]

    # Remove outlier frames based on dark pixel count
    frames = remove_outlier_frames(non_corrupt_frames, resize)

    if not frames:
        print("No valid frames were found after filtering.")
        return

    # ping pong playback - comment out if not desired
    frames = [frame for frame in frames]  # Copy frames into a list
    reversed_frames = frames[::-1][1:-1]  # Reverse the frames, excluding the first and last
    frames += reversed_frames             # Append the reversed frames to the original sequence

    # Save as a GIF
    frames[0].save(output_gif, save_all=True, append_images=frames[1:], optimize=True, duration=1000//frame_rate, loop=0, codec=codec)

    # Cleanup temporary directory
    for frame_file in frame_files:
        os.remove(frame_file)
    os.rmdir(temp_dir)

    print("Conversion done.")

def main():
    parser = argparse.ArgumentParser(description="Convert video to GIF with optional resizing and frame rate")
    parser.add_argument("input_video", help="Path to the input video file (.mov or .mp4)")
    parser.add_argument("output_gif", help="Path to the output GIF file")
    parser.add_argument("--resize", nargs=2, type=int, default=(1240, 720), metavar=("WIDTH", "HEIGHT"),
                        help="Resize the output GIF (default: 1240 720)")
    parser.add_argument("--frame-rate", type=int, default=12, metavar="FRAME_RATE",
                        help="Frame rate of the output GIF (default: 12)")

    args = parser.parse_args()

    input_video = args.input_video
    output_gif = args.output_gif
    resize = tuple(args.resize)
    frame_rate = args.frame_rate

    convert_video_to_gif(input_video, output_gif, resize=resize, frame_rate=frame_rate)

if __name__ == "__main__":
    main()
