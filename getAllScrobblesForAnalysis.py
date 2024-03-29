import pylast
import pandas as pd
import datetime
import time
def datefromtimecode(unixstring):
    ts=int(unixstring)
    return datetime.datetime.utcfromtimestamp(ts)

def getAlbumArtist(artist,album,network):
    album=pylast.Album(artist,album,network)
    return album.get_artist().name
def getTrackLength(ms):
    
    trackMin=ms//60000
    trackSec=int(ms%60000/1000)
    trackLength=f"{trackMin}:{trackSec}"
    return trackLength

def getScrobblesBetweenDates(userData,fromdate,todate):
    """
    Requires userData
    """
    datefrom=datetime.datetime.strptime(fromdate,"%d/%m/%Y")
    datefromUNIX=int(time.mktime(datefrom.timetuple()))

    dateto=datetime.datetime.strptime(todate,"%d/%m/%Y")
    datetoUNIX=int(time.mktime(dateto.timetuple()))
    library=userData.get_recent_tracks(limit=None,time_from=datefromUNIX, time_to=datetoUNIX)
    return library

def getScrobblesBeforeDate(userData,todate):
    """
    Requires userData
    """
    dateto=datetime.datetime.strptime(todate,"%d/%m/%Y %H:%M:%S")
    datetoUNIX=int(time.mktime(dateto.timetuple()))


    library=userData.get_recent_tracks(limit=200,time_to=datetoUNIX)
    return library

def getScrobblesByYear(userdata,year):
    datefrom=f"01/01/{year}"
    dateto=f"01/01/{year+1}"
    library=getScrobblesBetweenDates(userdata,datefrom,dateto)
    return library

def getArtistsAndPlayCounts(userdata):
    library=userData.get_library().get_artists(limit=None)
    return library

def newArtistDict(yearList,playcount):
    artist={"Total Count":playcount}
    for year in yearList:
        artist[str(year)]=0

    return artist

#api details
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

#first year is 2010
yearList=list(range(2023,2024))



todate="21/10/2023 00:00:00"
filename=None

#errorReported=False
#while not errorReported:
#get dates to look between in UNIX 
for year in yearList:
    scrobblelist=[]
    datefrom=datetime.datetime.strptime(f"01/01/{year}","%d/%m/%Y")
    datefromUNIX=int(time.mktime(datefrom.timetuple()))
    #print(datefromUNIX)
    dateto=datetime.datetime.strptime(f"01/01/{year+1}","%d/%m/%Y")
    datetoUNIX=int(time.mktime(dateto.timetuple()))
    #####
    #get tracks played in year
    lib=userData.get_recent_tracks(limit=None,time_from=datefromUNIX,time_to=datetoUNIX)
    # if errorReported:
    #     break
    for track in lib:
            
            
        tracktitle=track.track.title
        trackArtist=track.track.get_artist().name
        trackAlbum=track.album
        try:
            trackAlternativeAlbum=track.track.get_album()
        except:
            trackAlternativeAlbum = None
        if trackAlternativeAlbum is None:
            trackAlternativeAlbum=""
            trackAlternativeAlbumArtist=""
        else:
            try:
                trackAlternativeAlbum=track.track.get_album().title
                trackAlternativeAlbumArtist=track.track.get_album().get_artist().name
            except:
                print(f"{track.track.title} - {track.track.get_artist().name}")
                trackAlternativeAlbum=""
                trackAlternativeAlbumArtist=""
        
        
        scrobble={"Track":tracktitle,
                    "Artist":trackArtist,
                    "Album":track.album,
                    "Album Artist": getAlbumArtist(trackArtist,track.album,network),
                    'Alternative Album':trackAlternativeAlbum,
                    'Alternative Album Artist':trackAlternativeAlbumArtist,
                    'Scrobble Time': datefromtimecode(track.timestamp)
                    
                    
                    
                    
                    }
        scrobblelist.append(scrobble)
        
    
    #load in last got date
    #run process with this date plus new date getScrobblesBetweenDates()
    # get most recent date from library and pass back in



    # for year in yearList:
    #     lib=getScrobblesByYear(userData,year) # this will currently only get the last 200 of a year
    #     for track in lib:
            
            
    #         tracktitle=track.track.title
    #         trackArtist=track.track.get_artist().name
    #         trackAlbum=track.album
    #         trackAlternativeAlbum=track.track.get_album()
    #         if trackAlternativeAlbum is None:
    #             trackAlternativeAlbum=""
    #             trackAlternativeAlbumArtist=""
    #         else:
    #             try:
    #                 trackAlternativeAlbum=track.track.get_album().title
    #                 trackAlternativeAlbumArtist=track.track.get_album().get_artist().name
    #             except:
    #                 print(f"{track.track.title} - {track.track.get_artist().name}")
    #                 trackAlternativeAlbum=""
    #                 trackAlternativeAlbumArtist=""
            
            
    #         scrobble={"Track":tracktitle,
    #                   "Artist":trackArtist,
    #                   "Album":track.album,
    #                   "Album Artist": getAlbumArtist(trackArtist,track.album,network),
    #                   'Alternative Album':trackAlternativeAlbum,
    #                   'Alternative Album Artist':trackAlternativeAlbumArtist,
    #                   'Scrobble Time': datefromtimecode(track.timestamp)
                    
                    
                    
                    
    #                   }
    #         scrobblelist.append(scrobble)
    
    data=pd.DataFrame(scrobblelist)
    data=data.sort_values(by="Scrobble Time")
    
    n=datetime.datetime.now()
    datestr=n.strftime("%Y%m%d_%H%M%S")
    filename=f"AllScrobbles_{year}.csv"
    data.to_csv(filename,index=None)

    

    


    