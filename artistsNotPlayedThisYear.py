import pylast
import pandas as pd
import datetime
import time

#get year
year=datetime.datetime.today().year




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
#first get all artists in library

artistDict={}
library=userData.get_library().get_artists(limit=None)
for artist in library:

    workingArtist=artist.item.name
    
    artistDict[workingArtist]={f"{year} Count":0,
                                   "Total Count":artist.playcount}

#get dates to look between in UNIX 

datefrom=datetime.datetime.strptime(f"01/01/{year}","%d/%m/%Y")
datefromUNIX=int(time.mktime(datefrom.timetuple()))
#print(datefromUNIX)
dateto=datetime.datetime.strptime(f"01/01/{year+1}","%d/%m/%Y")
datetoUNIX=int(time.mktime(dateto.timetuple()))
#####
#get tracks played in year
yearlibrary=userData.get_recent_tracks(limit=None,time_from=datefromUNIX,time_to=datetoUNIX)
#cycle through details and get artists to get annual counts
for track in yearlibrary:

    workingArtist=track.track.get_artist().get_name()
    if workingArtist in artistDict:
        artistDict[workingArtist][f"{year} Count"]+=1
    else:
        artistDict[workingArtist]={f"{year} Count":1,
                                   "Total Count":0}


    


#convert to data frame

data=pd.DataFrame.from_dict(artistDict,orient='index')
#exclude where artists are played this year
data=data.loc[data[f"{year} Count"]==0]
data=data.reset_index()
data.to_csv(f"notplayed{year}.csv",index=None)
