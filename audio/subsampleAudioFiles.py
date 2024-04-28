import argparse
import os
from datetime import datetime
from pydub import AudioSegment

def sanitize_filename(filename):
    """Sanitizes filenames to remove spaces and problematic characters."""
    # Remove spaces and replace with underscores
    clean_filename = filename.replace(" ", "_")
    # todo: consolidate escape / nasty chars into a dict
    clean_filename = ''.join(char for char in clean_filename if char.isalnum() or char in "._-")
    return clean_filename

def normalize_audio(audio):
    """Normalizes the audio to a consistent perceived loudness."""
    return audio.normalize()

def extract_audio_snippet(input_dir, output_dir):
    """Extracts a 2-minute snippet from each audio file starting from 33% of its duration."""
    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(('.mp3', '.wav')):
            file_path = os.path.join(input_dir, file_name)
            audio = AudioSegment.from_file(file_path)

            start_time = int(len(audio) * 0.25)
            end_time = start_time + 90 * 1000  # N seconds in milliseconds

            # Clip the audio to not exceed the file's length
            snippet = audio[start_time:end_time]

            # Normalize the audio for consistent loudness
            snippet = normalize_audio(snippet)

            # Convert to mono and set to 64 kbps for file size optimization
            snippet = snippet.set_channels(1)
            snippet = snippet.set_frame_rate(22050)  # Lower sample rate to further reduce file size

            sanitized_file_name = sanitize_filename(f"snippet_{file_name}")
            output_file_path = os.path.join(output_dir, sanitized_file_name)
            snippet.export(output_file_path, format='mp3', bitrate='32k')

            print(f"Processed {file_name} and saved to {output_file_path}")

def main(input_dir):
    today_date = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(input_dir, f"processed_{today_date}")
    extract_audio_snippet(input_dir, output_dir)
    print(f"All files processed and saved in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract audio snippets from audio files.")
    parser.add_argument("input_dir", help="Input directory containing the audio files")

    args = parser.parse_args()

    main(args.input_dir)
