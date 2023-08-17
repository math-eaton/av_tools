import cv2
import os
from PIL import Image
import numpy as np
import subprocess

def create_video(image_files, video_path, fps, alpha_color=(255, 255, 255)):
    # Determine the width and height from the first image
    frame = Image.open(image_files[0])
    frame = frame.convert("RGBA")
    frame = Image.alpha_composite(Image.new("RGBA", frame.size, alpha_color), frame)
    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2BGR)

    height, width, channels = frame.shape

    # Define the codec and create a VideoWriter object
    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'H264'), fps, (width, height))

    for image in image_files:
        img = Image.open(image)
        img = img.convert("RGBA")
        img = Image.alpha_composite(Image.new("RGBA", img.size, alpha_color), img)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
        video.write(img)

    video.release()

image_folder = '/Users/matthewheaton/Documents/DOCENTS/lp1_design/assets/sorted_test'
image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png")])

video_path = "/Users/matthewheaton/Documents/DOCENTS/lp1_design/assets/cell_sample4.mp4"
fps = 12.0  # frames per second
create_video(image_files, video_path, fps, alpha_color=(255, 255, 255))  # white background
print("done with first pass")

def reencode_video(input_video_path, output_video_path):
    # Use ffmpeg to re-encode the video with VBR and overwrite if the output file already exists
    command = ['ffmpeg', '-y', '-i', input_video_path, '-vcodec', 'libx264', '-crf', str(crf), output_video_path]
    subprocess.run(command, check=True)

    # After re-encoding, delete the original video file
    if os.path.exists(input_video_path):  # always good to check if file exists before trying to delete
        os.remove(input_video_path)

input_video_path = "/Users/matthewheaton/Documents/DOCENTS/lp1_design/assets/sorted_test_vid/sample_threshold.mp4"
output_video_path = "/Users/matthewheaton/Documents/DOCENTS/lp1_design/assets/sorted_test_vid/sample_threshold_vbr.mp4"
crf = 40  # Constant Rate Factor for VBR, lower means better quality

reencode_video(input_video_path, output_video_path)
print("re-encoded video complete")

