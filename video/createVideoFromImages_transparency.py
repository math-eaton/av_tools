import os
import imageio.v2 as imageio
from tqdm import tqdm
import subprocess
import shutil
import tempfile

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

image_folder = '/Users/matthewheaton/Documents/DOCENTS/video/hotnose' 
image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png")])

# Take the first n images for testing results
image_files = image_files[:1000]

video_path = "/Users/matthewheaton/Documents/DOCENTS/video/hotnose/output/hotnose.webm"
create_video(image_files, video_path)
