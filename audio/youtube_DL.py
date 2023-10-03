import argparse
import yt_dlp
import re
import json

# Function to remove whitespace from a string
def remove_whitespace(s):
    return re.sub(r'\s', '', s)

def download_audio(input_source, output_dir, preferred_codec='mp3'):
    ydl_opts = {
        'format': f'{preferred_codec}/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_codec,
        }],
        'outtmpl': f'{output_dir}/{remove_whitespace("%(title)s.%(ext)s")}',  # Specify the output directory and sanitized filename template
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if input_source.startswith('http'):
            URLS = [input_source]
        else:
            with open(input_source, 'r') as file:
                data = json.load(file)
            URLS = [song["URL"] for song in data]

        error_code = ydl.download(URLS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Audio Downloader")
    parser.add_argument("--input-json", help="Input JSON file containing YouTube URLs")
    parser.add_argument("--youtube-url", help="Single YouTube URL to download")
    parser.add_argument("output_dir", help="Output directory for downloaded audio files")
    parser.add_argument("--preferred-codec", default="mp3", help="Preferred audio codec (default: mp3)")

    args = parser.parse_args()

    if args.input_json and args.youtube_url:
        print("Error: You can only specify one of input JSON or YouTube URL, not both.")
    elif not args.input_json and not args.youtube_url:
        print("Error: You must specify either input JSON or a YouTube URL.")
    else:
        if args.input_json:
            download_audio(args.input_json, args.output_dir, args.preferred_codec)
        else:
            download_audio(args.youtube_url, args.output_dir, args.preferred_codec)
