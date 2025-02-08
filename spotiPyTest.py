import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
load_dotenv()
client_id=os.getenv("CLIENT_ID")
client_secret=os.getenv("CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="https://www.bbc.co.uk/sport",
                                               scope="user-top-read"))

results = sp.current_user_top_artists(limit=50,time_range="long_term")
#print(results)
for idx, item in enumerate(results['items']):
    track = item['name']
    print(idx, track)