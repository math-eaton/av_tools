import os
import subprocess
import argparse

def convert_audio_files(input_directory, output_directory):
    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Iterate through each file in the directory
    for filename in os.listdir(input_directory):
        # Only process mp3 files
        if filename.endswith('.mp3'):
            # Create full file paths
            input_file_path = os.path.join(input_directory, filename)
            output_file_name = os.path.splitext(filename)[0] + '.ogg'  # Change extension to .ogg
            output_file_path = os.path.join(output_directory, output_file_name)

            # Construct the ffmpeg command to convert to ogg with low bitrate
            cmd = [
                'ffmpeg', 
                '-i', input_file_path, 
                '-acodec', 'libopus', 
                '-b:a', '64k',  # Low bitrate for small file size
                output_file_path
            ]

            # Execute the command
            subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Conversion Script")
    parser.add_argument("input_directory", help="Input directory")
    parser.add_argument("output_directory", nargs='?', help="Output directory (default: 'for_web' subfolder in input directory)")

    args = parser.parse_args()

    input_dir = args.input_directory
    output_dir = args.output_directory or os.path.join(input_dir, "for_web")

    convert_audio_files(input_dir, output_dir)
