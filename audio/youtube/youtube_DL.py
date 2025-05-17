import argparse
import yt_dlp
import re
import json
import os
import time
import random

def remove_whitespace(s):
    return re.sub(r'\s', '', s)

def download_audio(input_source, output_dir, preferred_codec='mp3', delay=1, is_playlist=False):
    ydl_opts = {
        'format': f'{preferred_codec}/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_codec,
            'preferredquality': '320',  # low quality '96' for space optimization - change to 320 for high quality
        }],
        'outtmpl': f'{output_dir}/{remove_whitespace("%(title)s.%(ext)s")}',
        'noplaylist': not is_playlist,  # True if downloading a single video, False if it's a playlist
        'ratelimit': 50 * 1024 * 1024,  # Limit the download rate to 50 MB/s
        'sleep_interval': delay,  # Time to wait before downloading the next video
        'max_sleep_interval': delay + 5,  # Maximum time to wait if yt-dlp decides to sleep longer
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        urls = [input_source] if input_source.startswith('http') else []
        if not urls:
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
    parser.add_argument("--yt-url", help="Single YouTube URL to download (in quotes)")
    parser.add_argument("--playlist", help="YouTube Playlist URL to download")
    parser.add_argument("output_dir", help="Output directory for downloaded audio files")
    parser.add_argument("--preferred-codec", default="mp3", help="Preferred audio codec (default: mp3)")
    parser.add_argument("--delay", type=int, default=5, help="Delay between downloads in seconds")

    args = parser.parse_args()

    if sum([bool(args.input_json), bool(args.yt_url), bool(args.playlist)]) != 1:
        print("Error: You must specify exactly one of input JSON, YouTube URL, or playlist.")
    else:
        if args.input_json:
            download_audio(args.input_json, args.output_dir, args.preferred_codec, args.delay)
        elif args.yt_url:
            download_audio(args.yt_url, args.output_dir, args.preferred_codec, args.delay)
        elif args.playlist:
            download_audio(args.playlist, args.output_dir, args.preferred_codec, args.delay, is_playlist=True)

