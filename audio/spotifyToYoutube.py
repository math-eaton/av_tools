import requests
from ratelimiter import RateLimiter
from config import SPOTIFY_TOKEN, YOUTUBE_API_KEY

PLAYLIST_ID = "35TjfHmu0EwC97hvKiaNy0"

# Function to get songs from Spotify
def get_spotify_songs():
    headers = {
        "Authorization": f"Bearer {SPOTIFY_TOKEN}"
    }

    response = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks", headers=headers)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

    data = response.json()

    songs = []

    for item in data['items']:
        track = item['track']
        artist = track['artists'][0]['name']
        song_name = track['name']
        songs.append(f"{artist} - {song_name}")

    return songs

# Rate limit YouTube search to once every 2 seconds
@RateLimiter(max_calls=1, period=2)
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

def main():
    songs = get_spotify_songs()
    youtube_links = {}

    for song in songs:
        print(f"Searching for {song}...")
        link = search_youtube(song)
        if link:
            youtube_links[song] = link
        else:
            print(f"Could not find YouTube link for {song}")

    print(youtube_links)

if __name__ == "__main__":
    main()
