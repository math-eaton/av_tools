import subprocess
import argparse
import os

def speed_up_video(input_video_path, output_video_path, speedup_factor):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-filter:v', f"setpts={1/speedup_factor}*PTS",
        output_video_path
    ]
    subprocess.run(command)

def resize_video(input_video_path, output_video_path, resolution):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-vf', f'scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,crop={resolution[0]}:{resolution[1]}',
        output_video_path
    ]
    subprocess.run(command)

def change_codec_and_bitrate(input_video_path, output_video_path, codec='libx264', bitrate='192k'):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-vcodec', codec,
        '-b:v', bitrate,
        output_video_path
    ]
    subprocess.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Processing Script")
    parser.add_argument("--input_video", required=True, help="Input video file path")
    parser.add_argument("--output_dir", help="Output directory for processed video. Default is the same as input directory.")
    parser.add_argument("--video_speed", type=float, default=1.0, help="Speed factor for the video (e.g., 2.0 for 2x speed)")
    parser.add_argument("--video_size", required=True, nargs=2, type=int, metavar=("WIDTH", "HEIGHT"), help="Output video size as WIDTH HEIGHT")
    parser.add_argument("--codec", default="libx264", help="Video codec (default: libx264)")
    parser.add_argument("--bitrate", default="192k", help="Video bitrate (default: 192k)")
    args = parser.parse_args()

    # Input video path
    input_video_path = args.input_video

    # Get the input video filename without extension
    input_filename = os.path.splitext(os.path.basename(input_video_path))[0]

    # Determine the output directory
    if args.output_dir:
        output_directory = args.output_dir
    else:
        # Use the same directory as the input video
        output_directory = os.path.dirname(input_video_path)

    # Create the output filename with "_processed" suffix
    output_filename = f"{input_filename}_processed.mp4"

    # Output video path
    output_video_path = os.path.join(output_directory, output_filename)

    # Apply transformations
    temp_path1 = "temp1.mov"
    temp_path2 = "temp2.mov"

    # Speed up the video
    speed_up_video(input_video_path, temp_path1, args.video_speed)

    # Resize the video
    resize_video(temp_path1, temp_path2, args.video_size)

    # Change codec and bitrate
    change_codec_and_bitrate(temp_path2, output_video_path, args.codec, args.bitrate)

    # Optional: Remove temporary files
    subprocess.run(['rm', temp_path1, temp_path2])

    print(f"Processed video saved to {output_video_path}")
