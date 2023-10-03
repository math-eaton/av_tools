import cv2
import os
from PIL import Image
import numpy as np
import subprocess
import argparse

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

def reencode_video(input_video_path, output_video_path, crf):
    # Use ffmpeg to re-encode the video with VBR and overwrite if the output file already exists
    command = ['ffmpeg', '-y', '-i', input_video_path, '-vcodec', 'libx264', '-crf', str(crf), output_video_path]
    subprocess.run(command, check=True)

    # After re-encoding, delete the original video file
    if os.path.exists(input_video_path):  # always good to check if file exists before trying to delete
        os.remove(input_video_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image to Video Conversion Script")
    parser.add_argument("--input_dir", required=True, help="Input directory containing image files")
    parser.add_argument("--output_dir", required=True, help="Output directory for the video file")
    parser.add_argument("--output_video_name", required=True, help="Name of the output video file")
    parser.add_argument("--framerate", type=float, default=13.0, help="Framerate for the output video (default: 13.0)")
    parser.add_argument("--alpha_color", nargs=3, type=int, default=[255, 255, 255], help="Alpha color as RGB values (default: 255 255 255)")
    parser.add_argument("--crf", type=int, default=20, help="Constant Rate Factor (CRF) for video encoding (default: 20)")
    args = parser.parse_args()

    # Input image folder
    image_folder = args.input_dir
    image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png")])

    # Output video path
    output_video_path = os.path.join(args.output_dir, args.output_video_name)

    # Create the video
    create_video(image_files, output_video_path, args.framerate, alpha_color=args.alpha_color)
    
    print("done with first pass")

    # Re-encode the video
    reencode_video(output_video_path, output_video_path.replace(".mp4", "_encoded.mp4"), args.crf)
    
    print("re-encoded video complete")
