## ------------------------------------------------------------ Imports ------------------------------------------------------------ ##
import os
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from time import sleep
load_dotenv()


## ------------------------------------------------------------ Constants ------------------------------------------------------------ ##
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

# Define the scope for permissions required
scope = "playlist-modify-public playlist-modify-private"


# ------------------------------------------------------------ Spotify Token Refresh  ------------------------------------------------------------ ##
# If your access token has expired, you can refresh it using the refresh token:
refresh_token_url = "https://accounts.spotify.com/api/token"
refresh_token_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
refresh_token_data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}
refresh_response = requests.post(url=refresh_token_url, headers=refresh_token_headers, data=refresh_token_data)
refreshed_token_info = refresh_response.json()
ACCESS_TOKEN = refreshed_token_info.get("access_token")


# ------------------------------------------------------------ Function to Search for Tracks on Spotify ------------------------------------------------------------ ##
def search_track(song_title, access_token):
    """Search for a song on Spotify and return the track URI"""
    search_url = f"https://api.spotify.com/v1/search?q={song_title}&type=track&limit=1"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(search_url, headers=headers)
    data = response.json()

    # Check if we have any results
    if data['tracks']['items']:
        track_uri = data['tracks']['items'][0]['uri']
        return track_uri
    else:
        return None


# ------------------------------------------------------------ Function to Add Tracks to Playlist ------------------------------------------------------------ ##
def add_tracks_to_playlist(playlist_id, track_uris, access_token):
    """Add tracks to a Spotify playlist"""
    add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "uris": track_uris
    }
    response = requests.post(add_tracks_url, headers=headers, json=payload)

    if response.status_code == 201:
        print(f"Successfully added {len(track_uris)} tracks to the playlist.")
    else:
        print(f"Failed to add tracks. Error: {response.status_code}")


# ------------------------------------------------------------ Main Function ------------------------------------------------------------ ##
def main():
    # Get the Billboard Top 100 songs for the date
    date = input("What point in time would you like to travel to (After 2020)? Type the date in this format YYYY-MM-DD: ")
    billboard_url = f"https://www.billboard.com/charts/hot-100/{date}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
    }
    response = requests.get(url=billboard_url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    song_elements = soup.select("div ul li ul li h3")
    song_titles = [song.getText().strip() for song in song_elements]
    print("Your playlist - ", song_titles)
    print("Go to:", billboard_url)

    # Create a playlist on Spotify
    create_playlist_url = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"
    playlist_data = {
        "name": f"Billboard Top 100 - {date.split('-')[0]}",
        "description": f"Top 100 songs from Billboard on {date}",
        "public": True
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url=create_playlist_url, headers=headers, json=playlist_data)
    playlist_info = response.json()

    # Extract the playlist URL
    playlist_url = playlist_info.get("external_urls", {}).get("spotify", "")
    if playlist_url:
        print(f"Creation in progress! You can access it here: {playlist_url}")
    else:
        print("Failed to create playlist or retrieve the URL.")

    # Search for each song and get the track URIs
    track_uris = []
    for song in song_titles:
        track_uri = search_track(song, ACCESS_TOKEN)
        if track_uri:
            track_uris.append(track_uri)
        else:
            print(f"Could not find track for: {song}")

    # Add the tracks to the playlist
    if track_uris:
        add_tracks_to_playlist(playlist_info['id'], track_uris, ACCESS_TOKEN)
    else:
        print("No tracks to add.")


# ------------------------------------------------------------ Calling the function ------------------------------------------------------------ ##
main()
print("Playlist created access by clicking the link above ⬆️")
