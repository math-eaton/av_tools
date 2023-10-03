import os
import subprocess
from PIL import Image
from tqdm import tqdm

def convert_mov_to_gif(input_mov, output_gif, resize=(1240, 720), frame_rate=12):
    # Create a temporary directory for frames
    temp_dir = "temp_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Convert the MOV to individual frames using ffmpeg
    subprocess.call([
        'ffmpeg',
        '-i', input_mov,
        '-r', str(frame_rate),  # Frame rate
        os.path.join(temp_dir, 'frame%04d.png')
    ])
    
    # Read all the frames
    frame_files = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir)])
    frames = [Image.open(f).convert('RGBA').resize(resize, Image.NEAREST) for f in tqdm(frame_files, desc="Reading frames")]

    # ping pong playback - comment out if not desired
    frames = [frame for frame in frames]  # Copy frames into a list
    reversed_frames = frames[::-1][1:-1]  # Reverse the frames, excluding the first and last
    frames += reversed_frames             # Append the reversed frames to the original sequence
    
    # Save as a GIF
    frames[0].save(output_gif, save_all=True, append_images=frames[1:], optimize=True, duration=1000//frame_rate, loop=0)

    # Cleanup temporary directory
    for frame_file in frame_files:
        os.remove(frame_file)
    os.rmdir(temp_dir)

    print("Conversion done.")


input_mov = "/Users/matthewheaton/Desktop/screenshot/Screen Recording 2023-08-12 at 4.19.20 PM.mov" 
output_gif = "/Users/matthewheaton/Documents/GSAPP_2022/GSAPP_summer_2023/slides/fm_newest.gif" 

convert_mov_to_gif(input_mov, output_gif)
