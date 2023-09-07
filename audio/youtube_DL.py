import yt_dlp
import re

# List of video URLs you want to download
URLS = ['https://www.youtube.com/watch?v=4vgcYBwyw28']

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
