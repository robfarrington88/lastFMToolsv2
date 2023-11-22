#this is now the library for all functions
import pylast
import pandas as pd
import datetime
import time, os
def datefromtimecode(unixstring):
    """ 
    Converts a Unixstring into a DateTime (UTC)
    """
    ts=int(unixstring)
    return datetime.datetime.utcfromtimestamp(ts)

def getAlbumArtist(artist,album,network):
    """
    gets an album Artist name from artist, album and network
    """
    album=pylast.Album(artist,album,network)
    return album.get_artist().name
def getTrackLength(ms):
    """
    Convert microsecond length of track into Min and Seconds as string
    """
    trackMin=ms//60000
    trackSec=int(ms%60000/1000)
    trackLength=f"{trackMin}:{trackSec}"
    return trackLength

def getScrobblesBetweenDates(userData,fromdate,todate):
    """
    Requires userData
    Get all scrobbles between from and to date in dmy format.
    """
    datefrom=datetime.datetime.strptime(fromdate,"%d/%m/%Y")
    datefromUNIX=int(time.mktime(datefrom.timetuple()))

    dateto=datetime.datetime.strptime(todate,"%d/%m/%Y")
    datetoUNIX=int(time.mktime(dateto.timetuple()))
    library=userData.get_recent_tracks(limit=None,time_from=datefromUNIX, time_to=datetoUNIX)
    return library

def getScrobblesBeforeDate(userData,todate):
    """
    get all scrobbles before a given date in dmy hms format.  Currently limited to 200
    """
    dateto=datetime.datetime.strptime(todate,"%d/%m/%Y %H:%M:%S")
    datetoUNIX=int(time.mktime(dateto.timetuple()))


    library=userData.get_recent_tracks(limit=200,time_to=datetoUNIX)
    return library

def getScrobblesByYear(userdata,year):
    """
    get all scrobbles in a given year (int)
    """
    datefrom=f"01/01/{year}"
    dateto=f"01/01/{year+1}"
    library=getScrobblesBetweenDates(userdata,datefrom,dateto)
    return library

def getArtistsAndPlayCounts(userdata):
    """
    get all artists and playcounts from userdata
    """
    library=userdata.get_library().get_artists(limit=None)
    return library

def newArtistDict(yearList,playcount):
    """
    create a new artist dictionary for storing annualised artist counts - this should now  not be required
    """
    artist={"Total Count":playcount}
    for year in yearList:
        artist[str(year)]=0

    return artist
def getNetwork():
    """
    Get LastFM network returns network and username
    """
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
    """
    Get USerData from network and username
    """
    username = "RobFarrington"
    userData = pylast.User(username, network)
    return userData

def getUpdate(filename):
    """
    Update a library CSV file from a filename which is datestamped. Returns the new data as a dataframe - feed into new item?
    """
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

def updateFile(filename):
    #filename="AllScrobblesTo_20231103_120805.csv"
    df=getUpdate(filename)


    dateparse = '%Y-%m-%d %H:%M:%S'

    updateDF = pd.read_csv(filename, date_format=dateparse)
    updateDF['Scrobble Time']=pd.to_datetime(updateDF['Scrobble Time'])

    updateDF=pd.concat([updateDF, df])

    updateDF=updateDF.sort_values(by="Scrobble Time")   
    updateDF.reset_index(drop=True,inplace=True)
    lastscrobble=updateDF.at[len(updateDF)-1,'Scrobble Time'].to_pydatetime().strftime("%Y%m%d_%H%M%S")
    updateDF.set_index('Scrobble Time',inplace=True)
    updatedFilename="AllScrobblesTo_"+lastscrobble+".csv"
    updateDF.to_csv(updatedFilename)
    return updatedFilename,updateDF

def loadDatabase(filename):
    """ loads Database as a df from csv file"""
    
    dateparse = '%Y-%m-%d %H:%M:%S'

    df = pd.read_csv(filename, date_format=dateparse)
    df['Scrobble Time']=pd.to_datetime(df['Scrobble Time'])
    df.set_index('Scrobble Time',inplace=True)
    return df

def annualCountsTable(df, fieldtype):
    """
    Gets annual counts for Album, Artist or Track required filenmae and either Artist"""
    
    keys=["Artist"]
    asKey=[False,True]
    if fieldtype in ["Track","Album"]:
        keys.append(fieldtype)
        asKey=[False,True,True]
    
        
    
        
    s=(df.pivot_table(index=keys,columns="Year",aggfunc=['size'],sort=True).fillna(0).astype(int))
    s=s.reset_index()

    s.columns = [f'{i}' if i != '' and j=='' else f'{j}' for i,j in s.columns]

    s['Total']=s[s.columns.to_list()[2:]].sum(axis=1)
    sortKeys=['Total']+keys
    s=s.sort_values(sortKeys,ascending=asKey)

    s.reset_index(inplace=True,drop=True)
    return s

def getAllAnnualCountsReports(filename):
    df=loadDatabase(filename)
    for key in ["Artist","Album","Track"]:
        pivot=annualCountsTable(df, key)
        pivot.to_csv(f"{key} Annual Counts.csv",index=False)
    
def getNotPlayedCurrentYear(df,key,year):
    pivot=annualCountsTable(df, key)
    
    unplayed=pivot.loc[pivot[year]==0]
    return unplayed

def getNotPlayedCurrentYearReports(filename):
    df=loadDatabase(filename)
    year=str(datetime.datetime.now().year)
    for key in ["Artist","Album","Track"]:
        unplayed=getNotPlayedCurrentYear(df,key,year)
    
        
        unplayed.to_csv(f"Unplayed{year}_{key}.csv",index=False)

def updateFilesandRefreshReports():
    currentfilename=getFileToUpdate()
    newfilename,df=updateFile(currentfilename)
    for key in ["Artist","Album","Track"]:
        pivot=annualCountsTable(df, key)
        pivot.to_csv(f"{key} Annual Counts.csv",index=False)
    year=str(datetime.datetime.now().year)
    for key in ["Artist","Album","Track"]:
        unplayed=getNotPlayedCurrentYear(df,key,year)
    
        
        unplayed.to_csv(f"Unplayed{year}_{key}.csv",index=False)
def getFileToUpdate():
    latestdate=datetime.datetime.min
    for file in os.listdir(os.curdir):
        if "AllScrobblesTo" in file:
            filename=os.path.splitext(file)[0]

            date=filename.split("_")[1:]
            date=datetime.datetime.strptime(date[0]+date[1],'%Y%m%d%H%M%S')
            if date>latestdate:
                latestdate=date
                filetouse=file
    return filetouse

def updateAllReports():
    network,username=getNetwork()
    ud=getUserData(network,username)

    #first year is 2010
    yearList=list(range(2010,2024))


    todate=datetime.datetime.today().strftime("%d/%m/%Y ")
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
        lib=ud.get_recent_tracks(limit=None,time_from=datefromUNIX,time_to=datetoUNIX)
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
          
        df=pd.DataFrame(scrobblelist)
        df=df.sort_values(by="Scrobble Time")
        
        
       
        filename=f"AllScrobbles_{year}.csv"
        df.to_csv(filename,index=None)
        if year==2010:
            fulldf=df
        else:
            fulldf=pd.concat([fulldf, df])



    fulldf=fulldf.sort_values(by="Scrobble Time")   
    fulldf.reset_index(drop=True,inplace=True)
    fulldf['Year']=fulldf['Scrobble Time'].apply(lambda x: x.year )
    lastscrobble=fulldf.at[len(fulldf)-1,'Scrobble Time'].to_pydatetime().strftime("%Y%m%d_%H%M%S")
    fulldf.set_index('Scrobble Time',inplace=True)
    fulldf.to_csv("AllScrobblesTo_"+lastscrobble+".csv")
    


    