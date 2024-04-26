import argparse
import yt_dlp
import re
import json
import os
import time
import random

def remove_whitespace(s):
    return re.sub(r'\s', '', s)

def download_audio(input_source, output_dir, preferred_codec='mp3', delay=5):
    ydl_opts = {
        'format': f'{preferred_codec}/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_codec,
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_dir}/{remove_whitespace("%(title)s.%(ext)s")}',
        'noplaylist': True,
        'ratelimit': 50 * 1024 * 1024,  # Limit the download rate to 50 MB/s
        'sleep_interval': delay,  # Time to wait before downloading the next video
        'max_sleep_interval': delay + 5,  # Maximum time to wait if yt-dlp decides to sleep longer
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if input_source.startswith('http'):
            urls = [input_source]
        else:
            with open(input_source, 'r') as file:
                data = json.load(file)
            urls = [song["URL"] for song in data]

        for url in urls:
            info_dict = ydl.extract_info(url, download=False)
            sanitized_title = remove_whitespace(info_dict.get('title', 'downloaded_audio'))
            output_file_path = os.path.join(output_dir, f"{sanitized_title}.{preferred_codec}")
            if os.path.exists(output_file_path):
                print(f"Skipping download, file already exists: {output_file_path}")
                continue

            # Random delay between downloads to reduce the risk of throttling
            time.sleep(random.randint(delay, delay + 5))

            # Download with retry logic
            try:
                ydl.download([url])
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                # Implement retry logic here if desired

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Audio Downloader")
    parser.add_argument("--input-json", help="Input JSON file containing YouTube URLs")
    parser.add_argument("--yt_url", help="Single YouTube URL to download")
    parser.add_argument("output_dir", help="Output directory for downloaded audio files")
    parser.add_argument("--preferred-codec", default="mp3", help="Preferred audio codec (default: mp3)")
    parser.add_argument("--delay", type=int, default=10, help="Delay between downloads in seconds")

    args = parser.parse_args()

    if args.input_json and args.yt_url:
        print("Error: You can only specify one of input JSON or YouTube URL, not both.")
    elif not args.input_json and not args.yt_url:
        print("Error: You must specify either input JSON or a YouTube URL.")
    else:
        if args.input_json:
            download_audio(args.input_json, args.output_dir, args.preferred_codec, args.delay)
        else:
            download_audio(args.yt_url, args.output_dir, args.preferred_codec, args.delay)

# example 
#  /Users/matthewheaton/micromamba/envs/creativeCoding/bin/python /Users/matthewheaton/Documents/GitHub/av_tools/audio/youtube_DL.py --yt_url "https://www.youtube.com/watch?v=NAgXG00Vhdk" "/Users/matthewheaton/Documents/GitHub/remotesensing/src/assets/sounds"