"""
Version 2 of the LastLib will include the following features:
- use of sqlite3 database to store data
- classes for album, artist, song, and scrobble
- functions to add scrobbles to the database
- functions to get data from the database
- Better analysis of data
https://stackoverflow.com/questions/2047814/is-it-possible-to-store-python-class-objects-in-sqlite
"""
import sqlite3
import datetime
import pylast
import time,os#
import json


"""
Existing Functionality:

This section includes existing functions from the old Last Library Module
"""
def getNetwork():
    """
    Get LastFM network returns network and username
    """
    #api details
    # You have to have your own unique two values for API_KEY and API_SECRET
    # Obtain yours from https://www.last.fm/api/account/create for Last.fm
    
    appsettings=os.path.join(os.path.dirname(__file__),"appsettings.json")
    with open(appsettings) as f:
        settings=json.load(f)
    network = pylast.LastFMNetwork(
        api_key=settings['API_KEY'],
        api_secret=settings['API_SECRET'],
        username=settings['username'],
        password_hash=pylast.md5(settings['password'])
        )
    username=settings['username']
    return network,username

def getUserData(network,username):
    """
    Get User Data from network and username
    """
    username = "RobFarrington"
    userData = pylast.User(username, network)
    return userData
def datefromtimecode(unixstring):
    """ 
    Converts a Unixstring into a DateTime (UTC)
    """
    ts=int(unixstring)
    return datetime.datetime.fromtimestamp(ts,datetime.timezone.utc)
    


def getAlbumArtist(artist,album,network):
    """
    gets an album Artist name from artist, album and network
    """
    album=pylast.Album(artist,album,network)
    return album.get_artist().name
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

def getScrobblesByYear(userdata,year):
    """
    get all scrobbles in a given year (int)
    """
    datefrom=f"01/01/{year}"
    dateto=f"01/01/{year+1}"
    library=getScrobblesBetweenDates(userdata,datefrom,dateto)
    return library

def scrobblesToDB(network,lib):
    #scrobblelist=[]
    artistsErrors={
        'The Pretenders':'Pretenders',
        'The Courteeners':'Courteeners',
        'Goo Goo Dolls'	: 'The Goo Goo Dolls',
        'The Nat King Cole Trio' :	'Nat King Cole Trio',
        'The Sisters of Mercy':'Sisters of Mercy'
        }
    conn,cursor=connectToDatabase('lastScrobbles.db')
    for track in lib:
        
        
        tracktitle=track.track.title
        trackArtist=track.track.get_artist().name
        trackAlbum=track.album

        # Consider a broader error processing module here. Maybe flag errors before entering library
        if trackArtist in artistsErrors.keys():
            trackArtist=artistsErrors[trackArtist]
        
        
        
        scrobble={"Track":tracktitle,
                    "Artist":trackArtist,
                    "Album":trackAlbum,
                    "Album Artist": getAlbumArtist(trackArtist,trackAlbum,network),
                    'Scrobble Time': datefromtimecode(track.timestamp),
                    'Year': datefromtimecode(track.timestamp).year
                    
                    
                    
                    
                    }
        #add direct to database here?
        
        add_scrobble(cursor,scrobble['Artist'],scrobble['Album'],scrobble['Track'],scrobble['Scrobble Time'])
    #data=pd.DataFrame(scrobblelist)
    commitAndClose(conn)
    return
def getAnnualScrobblesToDB(year):
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
    scrobblesToDB(network,lib)
    
    
    
    
    
    
# Connect to SQLite database (or create it if it doesn't exist)
def connectToDatabase(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    return conn, cursor
def commitAndClose(conn):
    conn.commit()
    conn.close()

def createDatabase():
    conn,cursor=connectToDatabase('lastScrobbles.db')
    


    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artist (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        rank_at INTEGER DEFAULT 0,
        scrobbles INTEGER DEFAULT 0,
        first_played TEXT,
        last_played TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS album (
        id INTEGER PRIMARY KEY,
        title TEXT,
        artist_id INTEGER,
        rank_at INTEGER DEFAULT 0,
        scrobbles INTEGER DEFAULT 0,
        first_played TEXT,
        last_played TEXT,
        FOREIGN KEY (artist_id) REFERENCES artist (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS song (
        id INTEGER PRIMARY KEY,
        title TEXT,
        artist_id INTEGER,
        album_id INTEGER,
        scrobbles INTEGER DEFAULT 0,
        first_played TEXT,
        last_played TEXT,
        FOREIGN KEY (artist_id) REFERENCES artist (id),
        FOREIGN KEY (album_id) REFERENCES album (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scrobble (
        id INTEGER PRIMARY KEY,
        artist_id INTEGER,
        album_id INTEGER,
        song_id INTEGER,
        timestamp TEXT,
        FOREIGN KEY (artist_id) REFERENCES artist (id),
        FOREIGN KEY (album_id) REFERENCES album (id),
        FOREIGN KEY (song_id) REFERENCES song (id)
    )
    ''')

# Function to add a scrobble
def add_scrobble(cursor,artist_name, album_title, song_title,scrobble_time):
    # Get current timestamp
    #scrobble_time = datetime.now().isoformat()

    # Check if artist exists
    cursor.execute('SELECT id, scrobbles, first_played, last_played FROM artist WHERE name = ?', (artist_name,))
    artist = cursor.fetchone()
    if artist:
        artist_id, artist_count, first_played,last_played = artist
        fp=datetime.datetime.strptime(first_played,"%Y-%m-%d %H:%M:%S%z")
        lp=datetime.datetime.strptime(last_played,"%Y-%m-%d %H:%M:%S%z")
        artist_count += 1
        if scrobble_time<fp:
            
            cursor.execute('UPDATE artist SET scrobbles = ?, first_played = ? WHERE id = ?', (artist_count, scrobble_time, artist_id))
        elif scrobble_time>lp:
            
            cursor.execute('UPDATE artist SET scrobbles = ?, last_played = ? WHERE id = ?', (artist_count, scrobble_time, artist_id))
        else:
            cursor.execute('UPDATE artist SET scrobbles = ? WHERE id = ?', (artist_count, artist_id))
    else:
        cursor.execute('INSERT INTO artist (name, scrobbles, first_played,last_played) VALUES (?, ?, ?, ?)', (artist_name, 1,scrobble_time, scrobble_time))
        artist_id = cursor.lastrowid

    # Check if album exists
    cursor.execute('SELECT id, scrobbles, first_played, last_played FROM album WHERE title = ? and artist_id = ?', (album_title,artist_id))
    album = cursor.fetchone()
    if album:
        album_id, album_count, first_played, last_played = album
        fp=datetime.datetime.strptime(first_played,"%Y-%m-%d %H:%M:%S%z")
        lp=datetime.datetime.strptime(last_played,"%Y-%m-%d %H:%M:%S%z")
        album_count += 1
        if scrobble_time<fp:
            
            cursor.execute('UPDATE album SET scrobbles = ?, first_played = ? WHERE id = ?', (album_count, scrobble_time, album_id))
        elif scrobble_time>lp:
            
            cursor.execute('UPDATE album SET scrobbles = ?, last_played = ? WHERE id = ?', (album_count, scrobble_time, album_id))
        else:
            cursor.execute('UPDATE album SET scrobbles = ? WHERE id = ?', (album_count, album_id))
    else:
        cursor.execute('INSERT INTO album (title, artist_id, scrobbles, first_played,last_played) VALUES (?, ?, ?, ?, ?)', (album_title,artist_id, 1,scrobble_time, scrobble_time))
        album_id = cursor.lastrowid

    # Check if song exists
    cursor.execute('SELECT id, scrobbles, first_played, last_played FROM song WHERE title = ? AND artist_id = ? AND album_id = ?', (song_title, artist_id, album_id))
    song = cursor.fetchone()
    if song:
        song_id, song_count,first_played,last_played = song
        fp=datetime.datetime.strptime(first_played,"%Y-%m-%d %H:%M:%S%z")
        lp=datetime.datetime.strptime(last_played,"%Y-%m-%d %H:%M:%S%z")
        song_count += 1
        if scrobble_time<fp:
            
            cursor.execute('UPDATE song SET scrobbles = ?, first_played = ? WHERE id = ?', (song_count, scrobble_time, song_id))
        elif scrobble_time>lp:
            
            cursor.execute('UPDATE song SET scrobbles = ?, last_played = ? WHERE id = ?', (song_count, scrobble_time, song_id))
        else:

            cursor.execute('UPDATE song SET scrobbles = ? WHERE id = ?', (song_count, song_id))
    else:
        cursor.execute('INSERT INTO song (title, artist_id, album_id, scrobbles, first_played, last_played) VALUES (?, ?, ?, ?, ?, ?)', 
                       (song_title, artist_id, album_id, 1, scrobble_time, scrobble_time))
        song_id = cursor.lastrowid

    # Add scrobble
    cursor.execute('INSERT INTO scrobble (artist_id,album_id,song_id, timestamp) VALUES (?, ?, ?, ?)', (artist_id,album_id,song_id, scrobble_time))

    
    

