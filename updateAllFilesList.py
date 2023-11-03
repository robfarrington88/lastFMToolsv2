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
    library=userdata.get_library().get_artists(limit=None)
    return library

def newArtistDict(yearList,playcount):
    artist={"Total Count":playcount}
    for year in yearList:
        artist[str(year)]=0

    return artist
def getNetwork():
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
    return network,username
def getUserData(network,username):
    username = "RobFarrington"
    userData = pylast.User(username, network)
    return userData

def getUpdate(filename):
    network,username=getNetwork()
    ud=getUserData(network,username)
    
    datefrom=datetime.datetime.strptime(filename[-19:-4],"%Y%m%d_%H%M%S")+datetime.timedelta(seconds=1)
    datefromUNIX=int(time.mktime(datefrom.timetuple()))
    #print(datefromUNIX)
    dateto=datetime.datetime.now()
    datetoUNIX=int(time.mktime(dateto.timetuple()))
    lib=ud.get_recent_tracks(limit=None,time_from=datefromUNIX,time_to=datetoUNIX)
    scrobblelist=[]
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
                    'Scrobble Time': datefromtimecode(track.timestamp),
                    'Year': datefromtimecode(track.timestamp).year
                    
                    
                    
                    
                    }
        scrobblelist.append(scrobble)
    data=pd.DataFrame(scrobblelist)
    data=data.sort_values(by="Scrobble Time")
    return data
    #first year is 2010

filename="AllScrobblesTo_20231102_114741.csv"
df=getUpdate(filename)


dateparse = '%Y-%m-%d %H:%M:%S'

fulldf = pd.read_csv(filename, date_format=dateparse)
fulldf['Scrobble Time']=pd.to_datetime(fulldf['Scrobble Time'])

fulldf=pd.concat([fulldf, df])

fulldf=fulldf.sort_values(by="Scrobble Time")   
fulldf.reset_index(drop=True,inplace=True)
lastscrobble=fulldf.at[len(fulldf)-1,'Scrobble Time'].to_pydatetime().strftime("%Y%m%d_%H%M%S")
fulldf.set_index('Scrobble Time',inplace=True)
fulldf.to_csv("AllScrobblesTo_"+lastscrobble+".csv")


    
    
    

    

    


    