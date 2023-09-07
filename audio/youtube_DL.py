import yt_dlp
import re
import json

# Load video URLs from free_samples.json
def load_urls_from_json(filename="audio/output/free_samples.json"):
    with open(filename, 'r') as file:
        data = json.load(file)
    return [song["url"] for song in data]

# List of video URLs you want to download
URLS = load_urls_from_json()

# Set the output directory
output_directory = 'audio/output/DL'

# Function to remove whitespace from a string
def remove_whitespace(s):
    return re.sub(r'\s', '', s)

ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    'outtmpl': f'{output_directory}/{remove_whitespace("%(title)s.%(ext)s")}',  # Specify the output directory and sanitized filename template
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download(URLS)
