import argparse
import os
import subprocess

def convert_gif_to_video(input_gif, output_video, codec='libx264', bitrate='1024k'):
    try:
        # Check if FFmpeg is available
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Run FFmpeg to convert the GIF to a video
        command = [
            'ffmpeg',
            '-i', input_gif,
            '-c:v', codec,
            '-b:v', bitrate,
            output_video
        ]
        subprocess.run(command, check=True)

        print(f"Video saved to '{output_video}'.")
    except FileNotFoundError:
        print("FFmpeg is not installed. Please install it to use this script.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a GIF to a web-compatible video format.")
    parser.add_argument("input_gif", help="Input GIF file path")
    parser.add_argument("output_video", help="Output video file path")
    parser.add_argument("--codec", default="libx264", help="Video codec (default: libx264)")
    parser.add_argument("--bitrate", default="1024k", help="Video bitrate (default: 1024k)")

    args = parser.parse_args()

    input_gif_path = args.input_gif
    output_video_path = args.output_video
    codec = args.codec
    bitrate = args.bitrate

    convert_gif_to_video(input_gif_path, output_video_path, codec, bitrate)
