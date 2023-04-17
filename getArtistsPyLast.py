import pylast
import pandas as pd
# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from https://www.last.fm/api/account/create for Last.fm
API_KEY = "e2630c64338004c988612946d2a12a44"  # this is a sample key
API_SECRET = "bb9d8b87ae6d5409f74b5cba14bcdf2b"

# In order to perform a write operation you need to authenticate yourself
username = "RobFarrington"
password_hash = pylast.md5("T0urmal=t")

network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=username,
    password_hash=password_hash,
)
userData = pylast.User(username, network)
library=userData.get_library().get_artists(limit=5000)
data=list()
for artist in library:

    data.append({"Artist":artist.item.name,"PlayCount":artist.playcount})



pd.DataFrame(data).to_csv('out.csv', index=False)
