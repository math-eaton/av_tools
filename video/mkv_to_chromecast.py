import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

def convert_mkv_for_chromecast(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,                # Input file
        '-c:v', 'libx264',               # Convert video to H.264
        '-preset', 'ultrafast',          # Faster encoding using the ultrafast preset
        '-crf', '23',                    # Constant Rate Factor (CRF) value
        '-c:a', 'aac',                   # Convert audio to AAC
        '-b:a', '192k',                  # Set audio bitrate to 192k
        '-movflags', '+faststart',       # Optimize MP4 for streaming
        '-threads', 'auto',              # Use automatic thread detection
        output_file                      # Output file
    ]
    subprocess.run(command)


if __name__ == "__main__":
    input_file = os.environ.get('MKV_INPUT') or input("Input MKV path: ")
    output_file = os.environ.get('MKV_OUTPUT') or input("Output MP4 path: ")
    convert_mkv_for_chromecast(input_file, output_file)
