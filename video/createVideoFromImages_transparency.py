import os
import imageio.v2 as imageio
from tqdm import tqdm
import subprocess
import shutil
import tempfile
import argparse

def create_video(image_files, video_path, frame_rate=13):
    # Create a temporary directory to store individual frames
    temp_dir = tempfile.mkdtemp()

    try:
        # Read images and save them as individual frames
        for i, image_file in enumerate(tqdm(image_files, desc="Reading images")):
            image = imageio.imread(image_file, mode='RGBA')
            frame_path = os.path.join(temp_dir, f'frame_{i:04d}.png')
            imageio.imwrite(frame_path, image)

        # Use FFmpeg to create a video from the individual frames
        # This example uses the WebM format with VP9 codec, preserving alpha channel
        ffmpeg_command = [
            'ffmpeg', 
            '-framerate', str(frame_rate),
            '-i', os.path.join(temp_dir, 'frame_%04d.png'),
            '-y',
            '-c:v', 'libvpx-vp9',
            '-pix_fmt', 'yuva420p',  # Use yuva420p pixel format for alpha channel
            '-b:v', '2M',  # Set video bitrate (adjust as needed)
            '-crf', '10',  # Set constant rate factor (adjust as needed)
            video_path
        ]
        subprocess.run(ffmpeg_command)
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

    print("done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image to Video Conversion Script")
    parser.add_argument("--input_dir", required=True, help="Input directory containing image files")
    parser.add_argument("--output_dir", required=True, help="Output directory for the video file")
    parser.add_argument("--output_video_name", required=True, help="Name of the output video file")
    parser.add_argument("--framerate", type=int, default=13, help="Framerate for the output video (default: 13)")
    args = parser.parse_args()

    # Input image folder
    image_folder = args.input_dir
    image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png")])

    # Output video path
    output_video_path = os.path.join(args.output_dir, args.output_video_name)

    # Create the video
    create_video(image_files, output_video_path, args.framerate)
