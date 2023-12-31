import os
import subprocess
import argparse

def convert_audio_files(input_directory, output_directory):
    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Iterate through each file in the directory
    for filename in os.listdir(input_directory):
        # Create full file paths
        input_file_path = os.path.join(input_directory, filename)
        output_file_name = os.path.splitext(filename)[0] + '.wav'  # Change extension to .wav
        output_file_path = os.path.join(output_directory, output_file_name)

        # Construct the SoX command
        cmd = [
            'sox', 
            input_file_path, 
            '-b', '24', 
            output_file_path, 
            'rate', '44.1k'
        ]

        # Execute the command
        subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Conversion Script")
    parser.add_argument("input_directory", help="Input directory")
    parser.add_argument("output_directory", nargs='?', help="Output directory (default: formatted_OT subfolder in input directory)")

    args = parser.parse_args()

    input_dir = args.input_directory
    output_dir = args.output_directory or os.path.join(input_dir, "formatted_OT")

    convert_audio_files(input_dir, output_dir)
