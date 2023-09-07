import requests
import json
from tenacity import retry, wait_fixed
from config import SPOTIFY_TOKEN, YOUTUBE_API_KEY

PLAYLIST_ID = "35TjfHmu0EwC97hvKiaNy0"

# Function to get songs from Spotify
def get_spotify_songs():
    headers = {
        "Authorization": f"Bearer {SPOTIFY_TOKEN}"
    }

    response = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks", headers=headers)
    response.raise_for_status()

    data = response.json()
    songs = []

    for item in data['items']:
        track = item['track']
        artist = track['artists'][0]['name']
        song_name = track['name']
        songs.append({"Artist": artist, "Song": song_name})

    return songs

# Rate limit YouTube search to once every 2 seconds
@retry(wait=wait_fixed(2))
def search_youtube(query):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": query,
        "key": YOUTUBE_API_KEY,
        "type": "video"
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()
    items = data.get('items', [])
    if items:
        video_id = items[0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def append_to_json(filepath, new_data):
    """Append data to a JSON file or create one if doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            current_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        current_data = []

    current_data.append(new_data)

    with open(filepath, 'w') as file:
        json.dump(current_data, file, indent=4)

def main():
    songs_data = get_spotify_songs()

    for song_data in songs_data:
        artist = song_data["Artist"]
        song_name = song_data["Song"]
        print(f"Searching for {artist} - {song_name}...")
        
        query = f"{artist} - {song_name}"
        link = search_youtube(query)
        
        if link:
            song_data["URL"] = link
            append_to_json("output/free_samples_2.json", song_data)
        else:
            print(f"Could not find YouTube link for {query}")

    print("Links saved to output/free_samples.json")

if __name__ == "__main__":
    main()