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

def findConsecutiveScrobbles(df):
    df=df.reset_index()
    df['check']=(df[['Track', 'Artist']] != df[['Track', 'Artist']].shift()).any(axis=1)
    df[df['check'] == False].to_csv("ConsecutiveScrobbles.csv")
    
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

def scrobblesToList(network,lib):
    scrobblelist=[]
    artistsErrors={
        'The Pretenders':'Pretenders',
        'The Courteeners':'Courteeners',
        'Goo Goo Dolls'	: 'The Goo Goo Dolls',
        'The Nat King Cole Trio' :	'Nat King Cole Trio',
        'The Sisters of Mercy':'Sisters of Mercy'
        }
    for track in lib:
        
        
        tracktitle=track.track.title
        trackArtist=track.track.get_artist().name
        trackAlbum=track.album
        if trackArtist in artistsErrors.keys():
            trackArtist=artistsErrors[trackArtist]
        
        
        
        scrobble={"Track":tracktitle,
                    "Artist":trackArtist,
                    "Album":trackAlbum,
                    "Album Artist": getAlbumArtist(trackArtist,trackAlbum,network),
                    'Scrobble Time': datefromtimecode(track.timestamp),
                    'Year': datefromtimecode(track.timestamp).year
                    
                    
                    
                    
                    }
        scrobblelist.append(scrobble)
    data=pd.DataFrame(scrobblelist)

    return data

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
    data=scrobblesToList(network,lib)
    if data.empty:
        return data
    data=data.sort_values(by="Scrobble Time")
    return data
    #first year is 2010

def updateFile(filename):
    import pytz
    #filename="AllScrobblesTo_20231103_120805.csv"
    df=getUpdate(filename)


    dateparse = '%Y-%m-%d %H:%M:%S'

    updateDF = pd.read_csv(filename, date_format=dateparse)
    updateDF['Scrobble Time']=pd.to_datetime(updateDF['Scrobble Time'])
    if not df.empty:
        updateDF=pd.concat([updateDF, df])

    updateDF=updateDF.sort_values(by="Scrobble Time")   
    updateDF.reset_index(drop=True,inplace=True)
    lastscrobble=updateDF.at[len(updateDF)-1,'Scrobble Time'].to_pydatetime()
    dt = datetime.datetime.now()
    
    timezone = pytz.timezone('Europe/London')
    if timezone.localize(lastscrobble).dst().total_seconds()>0:
        lastscrobble=lastscrobble+datetime.timedelta(hours=1)
    
    lastscrobble=lastscrobble.strftime("%Y%m%d_%H%M%S")
    updateDF.set_index('Scrobble Time',inplace=True)
    updatedFilename="AllScrobblesTo_"+lastscrobble+".csv"
    updateDF.to_csv(updatedFilename)
    deleteOldAllScrobbleFiles()
    return updatedFilename,updateDF

def loadDatabase(filename):
    """ loads Database as a df from csv file"""
    
    dateparse = '%Y-%m-%d %H:%M:%S'

    df = pd.read_csv(filename, date_format=dateparse)
    df['Scrobble Time']=pd.to_datetime(df['Scrobble Time'])
    df.set_index('Scrobble Time',inplace=True)
    df.fillna("",inplace=True)
    return df

def findBlanks(df):
    n=df.loc[df["Album"]==""]
    
    n.to_csv(f"Missing Album.csv")

def setupSortingKeys(fieldtype):
    keys=["Artist"]
    sortingLogic=[False,True]
    if fieldtype in ["Track","Album"]:
        keys.append(fieldtype)
        sortingLogic=[False,True,True]
    return(keys,sortingLogic)

def annualCountsTable(df, fieldtype):
    """
    Gets annual counts for Album, Artist or Track required filenmae and either Artist"""
    
    
    keys,asKey=setupSortingKeys(fieldtype)
    
        
    
        
    s=(df.pivot_table(index=keys,columns="Year",aggfunc=['size'],sort=True).fillna(0).astype(int))
    s=s.reset_index()

    s.columns = [f'{i}' if i != '' and j=='' else f'{j}' for i,j in s.columns]

    s['Total']=s[s.columns.to_list()[2:]].sum(axis=1)
    
    sortKeys=['Total']+keys
    s=s.sort_values(sortKeys,ascending=asKey)

    s.reset_index(inplace=True,drop=True)
    # if fieldtype=="Album":
    #     #this to add

    #     #the next phase of this is going to be get only for new albums.
    #     #load in album Counts
    #     countsTable=pd.read_csv('Album Annual Counts.csv')
        
    #     countsTable["ArtAlb"]=countsTable['Artist']+countsTable['Album']
    #     countsTable=countsTable[['ArtAlb','TrackCount']]

        
    #     #s=s[['Artist','Album','Total']]
    #     s["ArtAlb"]=s['Artist']+s['Album']
    #     #mergeTables
    #     checkTable=s.merge(countsTable, how='left',on='ArtAlb')
    #     #at2=s[['Artist','Album']]
    #     #at2=s.iloc[0:10,0:2]
    #     missingTable=checkTable.loc[pd.isna(checkTable['TrackCount'])]
    #     aadict=missingTable.to_dict()
    #     artistDict=aadict['Artist']
    #     albumDict=aadict['Album']
    #     countdict={}
    #     net,un=getNetwork()
    #     for k,v in artistDict.items():
    #         countdict[k]=addTrackCount(artistDict[k],albumDict[k],net,un)
    #     countDF=pd.DataFrame({'Artist':artistDict,'Album':albumDict,'TrackCount':countdict})
    #     countDF["ArtAlb"]=countDF['Artist']+countDF['Album']
    #     checkTable.update(countDF)
    #     s=checkTable[['Artist', 'Album', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024','2025', 'Total', 'TrackCount']]
    return s

def lastPlayed(df, fieldtype):
    keys,_=setupSortingKeys(fieldtype)

    """ Gives last time each track, album, artist was played, compared with total counts. """
    c=df.reset_index()
    a=c.groupby(keys).size().reset_index()
    b=c.groupby(keys).last().reset_index()
    a["Plays"]=a[0]
    
    if fieldtype!="Artist":
        a["newInd"]=a[keys[1]]+a[keys[0]]
        b["newInd"]=b[keys[1]]+b[keys[0]]
        a=a[["newInd","Plays"]]
        fields=["newInd"]+keys+["Scrobble Time"]
        b=b[fields]

        new=pd.merge(b,a,how="inner",left_on="newInd",right_on="newInd")
        new=new.drop(columns=["newInd"])
    else:
        a=a[[fieldtype,"Plays"]]
        b=b[["Artist","Scrobble Time"]]
        new=pd.merge(b,a,how="inner",left_on=fieldtype,right_on=fieldtype)
        

        

    
    new=new.sort_values(by=["Scrobble Time"],ascending=True)
    new.to_csv(fieldtype+"_LastPlayedReport.csv", index=False)

def getAllAnnualCountsReports(filename):
    df=loadDatabase(filename)
    for key in ["Artist","Album","Track"]:
        pivot=annualCountsTable(df, key)
        pivot.to_csv(f"{key} Annual Counts.csv",index=False)

def getNotPlayedDecade(df):
    keys=["Artist","Album","Track"]
    asKey=[True,True,True]
    
    
    
        
    
        
    s=(df.pivot_table(index=keys,columns="Year",aggfunc=['size'],sort=True).fillna(0).astype(int))
    s=s.reset_index()

    s.columns = [f'{i}' if i != '' and j=='' else f'{j}' for i,j in s.columns]

    s['Total']=s[s.columns.to_list()[3:]].sum(axis=1)
    
  
    pivot=s.sort_values(keys,ascending=asKey)

    pivot.reset_index(inplace=True,drop=True)
    
    unplayed=pivot.loc[(pivot['2020']==0) & (pivot['2021']==0) &(pivot['2022']==0) &(pivot['2023']==0) &(pivot['2024']==0) &(pivot['2025']==0) ]
    unplayed=unplayed.sort_values(keys,ascending=asKey)
    unplayed.to_csv(f"NotPlayed2020s.csv",index=False)

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


def deleteOldAllScrobbleFiles():
    currentfilename=getFileToUpdate()
    for root,dirs,files in os.walk(os.curdir):
        for filename in files:
            if "AllScrobblesTo" in filename and currentfilename not in filename:
                os.remove(filename)

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
        lastPlayed(df, key)
    getNotPlayedDecade(df)
    findBlanks(df)
    findConsecutiveScrobbles(df)
    duplicateAlbumsForTrack(df)
    #incompleteAlbums2(df)
    #incompleteAlbums(df)
    #run last
    reportPotentialErrors(df)
    
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

def updateYearCSV(year):
    network,username=getNetwork()
    ud=getUserData(network,username)

    #first year is 2010
    if year<2010:
        return



    

    #errorReported=False
    #while not errorReported:
    #get dates to look between in UNIX 
   
    
    lib=getScrobblesByYear(ud,year)
    # if errorReported:
    #     break
    df=scrobblesToList(network,lib)
    
    df=df.sort_values(by="Scrobble Time")
    
    
    
    filename=f"AllScrobbles_{year}.csv"
    df.to_csv(filename,index=None)


def duplicateAlbumsForTrack(df):
    counts=pd.DataFrame(df.groupby(['Artist','Track'])['Album'].nunique())
    counts=counts.rename(columns={'Album':'Album Count'})
    multiple_albums=counts.loc[counts['Album Count']>1]
    names=pd.DataFrame(df.groupby(['Artist','Track'])['Album'].unique())
    names=names.reset_index()
    names=names.rename(columns={'Album':'Album Names'})
    multiple_albums=multiple_albums.reset_index()
    names["ArtTrack"]=names['Artist']+names['Track']
    multiple_albums["ArtTrack"]=multiple_albums['Artist']+multiple_albums['Track']
    multiple_albums=multiple_albums.set_index("ArtTrack")
    names=names.set_index("ArtTrack")

    frame=multiple_albums.merge(names['Album Names'],left_index=True,right_index=True,how='left')
    frame=frame.reset_index()

    
    frame[['Artist','Track','Album Names']].to_csv("DuplicateAlbumsForTracks.csv")

    
def updateAllYears():
    network,username=getNetwork()
    ud=getUserData(network,username)

    #first year is 2010
    #FUTURE: set so last year here is current+1
    yearList=list(range(2010,2026))


    todate=datetime.datetime.today().strftime("%d/%m/%Y ")
    
    filename=None

    #errorReported=False
    #while not errorReported:
    #get dates to look between in UNIX 
    for year in yearList:
        
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
        df=scrobblesToList(network,lib)
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

def joinAnnualReports():
    firstFile=True
    fulldf=None
    folderpath=r"C:\Users\robfa\Documents\Coding\Github\lastFMToolsv2"
    dateparse = '%Y-%m-%d %H:%M:%S'

   

    for root,dir,files in os.walk(folderpath):
        for file in files:
            if "AllScrobbles_" in file:
                filepath=os.path.join(folderpath,file)
                df=pd.read_csv(filepath, date_format=dateparse)
                df['Scrobble Time']=pd.to_datetime(df['Scrobble Time'])
                if firstFile:
                    fulldf=pd.DataFrame(columns=df.columns)
                    firstFile=False
                fulldf=pd.concat([fulldf, df])
    fulldf=fulldf.sort_values(by="Scrobble Time")   
    fulldf.reset_index(drop=True,inplace=True)
    fulldf['Year']=fulldf['Scrobble Time'].apply(lambda x: x.year )
    lastscrobble=fulldf.at[len(fulldf)-1,'Scrobble Time'].to_pydatetime().strftime("%Y%m%d_%H%M%S")
    fulldf.set_index('Scrobble Time',inplace=True)
    fulldf.to_csv("AllScrobblesTo_"+lastscrobble+".csv")

def reportPotentialErrors(df2):
    df=df2
    df['ErrorFound']=False
    df['TrackErrorFound']=False
    df['ArtistErrorFound']=False
    df['AlbumErrorFound']=False
    df['AlbumArtistErrorFound']=False
    #r"([/-] .*)? ?(Deluxe|Platinum|Anniversary|Hidden Track|Collection|Acoustic|Acústico).*| [(\\[][^()\\[\\]]*?(Deluxe|Platinum|Acoustic|Live|Ao vivo|Acústico|Collection|Feat.|Feat|Hidden Track|Remix|With|Mono|Anniversary|Stereo|Master|Ft.|Featuring|Radio)[^()\\[\\]]*[)\\]]",
    # trackErrorList=[
    #        r" [(\\[][^()\\[\\]]*?(Deluxe|Platinum|Acoustic|Live|Ao vivo|Acústico|Collection|Feat.|Feat|Hidden Track|Remix|With|Mono|Anniversary|Stereo|Master|Ft.|Featuring|Radio)[^()\\[\\]]*[)\\]]",
    #        r" *?(- single|- live|- acoustic|- ao vivo|- acústico).*| [(\\[][^()\\[\\]]*?(- single|- live|- acoustic|- ao vivo|- acústico)[^()\\[\\]]*[)\\]]",
    #        r" [(\\[][^()\\[\\]]*?re-?mastere?d?[^()\\[\\]]*[)\\]]| ([/-] )?([(\\[]?\\d+[)\\]]?)? ?re-?mastere?d? ?(version)?([(\\[]?\\d+[)\\]]?)?",
    #        r" [(\\[][^()\\[\\]]*?(explicit|clean)[^()\\[\\]]*[)\\]]",
    #        r" ([/-] )? ?bonus.*(.*?version)?| [(\\[][^()\\[\\]]*?bonus[^()\\[\\]]*[)\\]]",
    #        ' / ',
    #        r" ([/-] .*)? ?(Edition).*| [(\\[][^()\\[\\]]*?(Edition)[^()\\[\\]]*[)\\]]",
    #        r" [/-] .* ?(Deluxe|Platinum|Anniversary|Hidden Track|Collection|Acoustic|Acústico|Radio|Master|Edit|Version|Dirty|explicit|Mono|Stereo).*",
    #        '’',
    #        r"[(\[].*Version(?<!Taylor's Version)[)\]]",
    #        r" ([/-] )?from.*?soundtrack",
    #        r" ([/-] )?([(\\[])?(music )?(theme )?from \".*\".*([)\\]])?",
    #        r" ([/-] )?([(\\[])?((theme|music) )?from .*motion picture.*([)\\]])?"
    # ]
    # albumErrorList=[
    #        r" [(\\[][^()\\[\\]]*?(Deluxe|Platinum|Acoustic|Live|Ao vivo|Acústico|Collection|Feat.|Feat|Hidden Track|Remix|With|Mono|Anniversary|Stereo|Master|Ft.|Featuring|Radio)[^()\\[\\]]*[)\\]]",
    #        r" *?(- single|- live|- acoustic|- ao vivo|- acústico).*| [(\\[][^()\\[\\]]*?(- single|- live|- acoustic|- ao vivo|- acústico)[^()\\[\\]]*[)\\]]",
    #        r" [(\\[][^()\\[\\]]*?re-?mastere?d?[^()\\[\\]]*[)\\]]| ([/-] )?([(\\[]?\\d+[)\\]]?)? ?re-?mastere?d? ?(version)?([(\\[]?\\d+[)\\]]?)?",
    #        r" [(\\[][^()\\[\\]]*?(explicit|clean)[^()\\[\\]]*[)\\]]",
    #        r" ([/-] )? ?bonus.*(.*?version)?| [(\\[][^()\\[\\]]*?bonus[^()\\[\\]]*[)\\]]",
    #        ' / ',
    #        r" ([/-] .*)? ?(Edition).*| [(\\[][^()\\[\\]]*?(Edition)[^()\\[\\]]*[)\\]]",
    #        r" [/-] .* ?(Deluxe|Platinum|Anniversary|Hidden Track|Feat|Collection|Acoustic|Acústico|Radio|Master|Edit|Version|Dirty|explicit|Mono|Stereo!p).*",
    #        '’',
    #        r"[(\\[].*Version(?<!Taylor's Version)[)\\]]"
    # ]
    # artistErrorList=[
    #        r"([/-])?(,) (?!Creator|Yeah|the Bad|Stills|Nash|Skinner|Paul|Lake|Wind).*",
    #        '’'
    # ]
    #New version - search for much more general errors to try and identify more appropriate regex/order

    trackErrorList=[
        r"([\[]|[(])",
        ' / ',
        '’',
        r" [/-] "
    ]
    albumErrorList=[
        r"([\[]|[(])",
        ' / ',
        '’',
        r" [/-] "
    ]
    artistErrorList=[
        r"([/-])?(,) "
    ]
    #df.loc[df['Track'].str.contains('’'),'ErrorFound']=True
    #track errors
    for error in trackErrorList:
        print(error)
        df.loc[df['Track'].str.contains(error),'TrackErrorFound']=True
        df.loc[df['Track'].str.contains(error),'ErrorFound']=True
    for error in albumErrorList:
        print(error)
        tmp=df.loc[~df['Album'].isna()]
        s=tmp.loc[tmp['Album'].str.contains(error)]
        if not s.empty:

            df.loc[s.index,'AlbumErrorFound']=True
            df.loc[s.index,'ErrorFound']=True
    for error in artistErrorList:
        print(error)
        df.loc[df['Artist'].str.contains(error),'ArtistErrorFound']=True
        df.loc[df['Artist'].str.contains(error),'ErrorFound']=True
        df.loc[df['Album Artist'].str.contains(error),'AlbumArtistErrorFound']=True
        df.loc[df['Album Artist'].str.contains(error),'ErrorFound']=True
    df2=df.loc[df['ErrorFound']==True]
    df2.to_csv("PotentialErrors.csv")

def getTracksInAlbums(df):
    from datetime import datetime
    startTime = datetime.now()
    #the next phase of this is going to be get only for new albums.
    #load in album Counts
    countsTable=pd.read_csv('AlbumCounts.csv')
    
    countsTable["ArtAlb"]=countsTable['Artist']+countsTable['Album']
    countsTable=countsTable[['ArtAlb','TrackCount']]

    albumTable=annualCountsTable(df, 'Album')
    albumTable=albumTable[['Artist','Album','Total']]
    albumTable["ArtAlb"]=albumTable['Artist']+albumTable['Album']
    #mergeTables
    checkTable=albumTable.merge(countsTable, how='left',on='ArtAlb')
    #at2=albumTable[['Artist','Album']]
    #at2=albumTable.iloc[0:10,0:2]
    missingTable=checkTable.loc[pd.isna(checkTable['TrackCount'])]
    aadict=missingTable.to_dict()
    artistDict=aadict['Artist']
    albumDict=aadict['Album']
    countdict={}
    net,un=getNetwork()
    for k,v in artistDict.items():
        countdict[k]=addTrackCount(artistDict[k],albumDict[k],net,un)
    countDF=pd.DataFrame({'Artist':artistDict,'Album':albumDict,'TrackCount':countdict})
    countDF["ArtAlb"]=countDF['Artist']+countDF['Album']
    checkTable.update(countDF)


    print(datetime.now() - startTime)
    nowtime=datetime.now().strftime("%Y%m%d_%H%M%S")
    #albumTable['NoTracks']=albumTable.apply(lambda x: addTrackCount(x['Artist'],x['Album'],0),axis=1)
    #albumTable['TrackCount']=albumTable.apply(lambda x: addTrackCount(x['Artist'],x['Album'],3),axis=1)
    checkTable[['Artist','Album','TrackCount']].to_csv(f"AlbumCounts_{nowtime}.csv")
    #order album in library by number 
    
def applyMetric(x):
    if x['incompleteAlbum']:
        metric=0
    else:
        avPlays=['Track']
    
def getLFAlbumTracks(artist,albumName,net,un):
    
    album=pylast.Album(artist,albumName,net,un,'info')
    tracks=[]
    try:
        trackLF=album.get_tracks()

        for track in trackLF:
            tracks.append(track.title)
    except:
        #when no album
        tracks=[]
    
    # trackCountList=[]
    # for track in album.get_tracks():
    #     trackCountList.append(track.get_userplaycount())
    # trackCountList.sort(reverse=True)
    # mostPlayed=trackCountList[0]
    # leastPlayed=trackCountList[trackCount-1]
    # totalPlays=sum(trackCountList[0:trackCount])
    # avPlays=totalPlays/(trackCount*1.0)
    # incompleteAlbum=False
    # if leastPlayed==0:
    #     incompleteAlbum=True
    # score=leastPlayed*100+(totalPlays-leastPlayed*trackCount)*10
    return tracks
    
def addTrackCount(artist,albumName,net,un):
    
    album=pylast.Album(artist,albumName,net,un,'info')
    try:
        trackCount=len(album.get_tracks())
    except:
        #when no album
        trackCount=-1
    
    # trackCountList=[]
    # for track in album.get_tracks():
    #     trackCountList.append(track.get_userplaycount())
    # trackCountList.sort(reverse=True)
    # mostPlayed=trackCountList[0]
    # leastPlayed=trackCountList[trackCount-1]
    # totalPlays=sum(trackCountList[0:trackCount])
    # avPlays=totalPlays/(trackCount*1.0)
    # incompleteAlbum=False
    # if leastPlayed==0:
    #     incompleteAlbum=True
    # score=leastPlayed*100+(totalPlays-leastPlayed*trackCount)*10
    return trackCount

def incompleteAlbums(df):
    #keys,asKey=ll.setupSortingKeys('Track')
    #s=(df.pivot_table(index=keys,columns="Album",aggfunc=['size'],sort=True).fillna(0).astype(int))
    frame=df.groupby(['Artist','Album'])['Track'].nunique()
    frame=frame.reset_index()
    frame=frame.sort_values(by='Track',ascending=False)
    net,un=getNetwork()
    
    #probably want to have a join with some sort of albums definitely played list. Either ones which we have from this report
    artists=frame['Artist'].to_list()
    albums=frame['Album'].to_list()
    trackUnique=frame['Track'].to_list()
    unplayedsongs=[]
    for i in range(0,len(artists)):
        if trackUnique[i]<5:
            break
        

        songs=getLFAlbumTracks(artists[i],albums[i],net,un)
        playedsongs=df.loc[(df['Artist']==artists[i]) & (df['Album']==albums[i])].groupby(['Artist','Album'])['Track'].unique()[0].tolist()
        songs2=[x.lower() for x in songs]
        playedsongs2=[x.lower() for x in playedsongs]
        unplayedsongtitles=list(set(songs2).difference(set(playedsongs2)))
        #will later want to define the difference here
        for song in unplayedsongtitles:
            unplayedsong={
                        "Artist":artists[i],
                        "Album":albums[i],
                        "Track":song
                    }
            unplayedsongs.append(unplayedsong)
    data=pd.DataFrame(unplayedsongs)
    old=pd.read_csv('Album Annual Counts.csv')
    #old=old[['Artist','Album','TrackCount']]
    #frame.update(old)
    old["ArtAlb"]=old['Artist']+old['Album']
    data["ArtAlb"]=data['Artist']+data['Album']
    data=data.set_index("ArtAlb")
    old=old.set_index("ArtAlb")

    frame=data.merge(old[['TrackCount','Total']],left_index=True,right_index=True)
    frame=frame.reset_index()
    frame=frame.drop(columns=['ArtAlb'])
    #frame=frame.rename(columns={'Track':'UniqueTracksPlayed'})

    #incomplete=frame.loc[frame['UniqueTracksPlayed']<frame['TrackCount']]
    frame=frame.sort_values(by='Total',ascending=False)
    frame.to_csv("SongsToPlay_byAlbumCount.csv", index=False)
    s=pd.DataFrame(df.groupby(['Artist']).size(),columns=['ArtistCount'])
    frame2=frame.merge(s,left_on="Artist",right_on="Artist",how='left')
    incomplete=frame2.sort_values(by='ArtistCount',ascending=False)
    incomplete.to_csv("SongsToPlay_byArtistCount.csv", index=False)
    
def incompleteAlbums2(df):
    #keys,asKey=ll.setupSortingKeys('Track')
    #s=(df.pivot_table(index=keys,columns="Album",aggfunc=['size'],sort=True).fillna(0).astype(int))
    frame=df.groupby(['Artist','Album'])['Track'].nunique()
    frame=frame.reset_index()

    #frame['TrackCount']=pd.NA
    #old version
    old=pd.read_csv('Album Annual Counts.csv')
    #old=old[['Artist','Album','TrackCount']]
    #frame.update(old)
    old["ArtAlb"]=old['Artist']+old['Album']
    frame["ArtAlb"]=frame['Artist']+frame['Album']
    frame=frame.set_index("ArtAlb")
    old=old.set_index("ArtAlb")

    frame=frame.merge(old[['TrackCount','Total']],left_index=True,right_index=True)
    frame=frame.reset_index()
    frame=frame.drop(columns=['ArtAlb'])
    frame=frame.rename(columns={'Track':'UniqueTracksPlayed'})

    incomplete=frame.loc[frame['UniqueTracksPlayed']<frame['TrackCount']]
    incomplete=incomplete.sort_values(by='Total',ascending=False)
    incomplete.to_csv("IncompleteAlbums_byAlbumCount.csv", index=False)
    s=pd.DataFrame(df.groupby(['Artist']).size(),columns=['ArtistCount'])
    incomplete2=incomplete.merge(s,left_on="Artist",right_on="Artist",how='left')
    incomplete=incomplete2.sort_values(by='ArtistCount',ascending=False)
    incomplete.to_csv("IncompleteAlbums_byArtistCount.csv", index=False)
    