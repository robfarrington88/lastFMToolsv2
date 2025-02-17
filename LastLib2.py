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
from datetime import datetime
import pylast
import time,os


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
    return datetime.datetime.utcfromtimestamp(ts)

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
        scrobblelist.append(scrobble)
    data=pd.DataFrame(scrobblelist)

    return data

# Connect to SQLite database (or create it if it doesn't exist)
def connectToDatabase(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    return conn, cursor
def createDatabase():
    conn,cursor=connectToDatabase('lastScrobbles.db')
    


    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artist (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        rank_at INTEGER DEFAULT 0,
        play_count INTEGER DEFAULT 0,
        first_played TEXT,
        last_played TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS album (
        id INTEGER PRIMARY KEY,
        title TEXT UNIQUE,
        artist_id INTEGER,
        rank_at INTEGER DEFAULT 0,
        play_count INTEGER DEFAULT 0,
        first_played TEXT,
        last_played TEXT,
        FOREIGN KEY (artist_id) REFERENCES artist (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS song (
        id INTEGER PRIMARY KEY,
        title TEXT UNIQUE,
        artist_id INTEGER,
        album_id INTEGER,
        play_count INTEGER DEFAULT 0,
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
def add_scrobble(cursor,conn,artist_name, album_title, song_title,scrobble_time,):
    # Get current timestamp
    #scrobble_time = datetime.now().isoformat()

    # Check if artist exists
    cursor.execute('SELECT id, count FROM artist WHERE name = ?', (artist_name,))
    artist = cursor.fetchone()
    if artist:
        artist_id, artist_count = artist
        artist_count += 1
        cursor.execute('UPDATE artist SET count = ?, last_played = ? WHERE id = ?', (artist_count, scrobble_time, artist_id))
    else:
        cursor.execute('INSERT INTO artist (name, count, first_played,last_played) VALUES (?, ?, ?)', (artist_name, 1,scrobble_time, scrobble_time))
        artist_id = cursor.lastrowid

    # Check if album exists
    cursor.execute('SELECT id, count FROM album WHERE title = ?', (album_title,))
    album = cursor.fetchone()
    if album and artist_id == album[1]:
        album_id, album_count = album
        album_count += 1
        cursor.execute('UPDATE album SET count = ?, last_played = ? WHERE id = ?', (album_count, scrobble_time, album_id))
    else:
        cursor.execute('INSERT INTO album (title, artist_id, count, first_played,last_played) VALUES (?, ?, ?)', (album_title,artist_id, 1,scrobble_time, scrobble_time))
        album_id = cursor.lastrowid

    # Check if song exists
    cursor.execute('SELECT id, count FROM song WHERE title = ? AND artist_id = ? AND album_id = ?', (song_title, artist_id, album_id))
    song = cursor.fetchone()
    if song and artist_id == song[1]:
        song_id, song_count = song
        song_count += 1
        cursor.execute('UPDATE song SET count = ?, last_played = ? WHERE id = ?', (song_count, scrobble_time, song_id))
    else:
        cursor.execute('INSERT INTO song (title, artist_id, album_id, count, first_played, last_played) VALUES (?, ?, ?, ?, ?)', 
                       (song_title, artist_id, album_id, 1, scrobble_time, scrobble_time))
        song_id = cursor.lastrowid

    # Add scrobble
    cursor.execute('INSERT INTO scrobble (artist_id,album_id,song_id, timestamp) VALUES (?, ?)', (artist_id,album_id,song_id, scrobble_time))

    # Commit changes
    conn.commit()
    conn.close()

# Example usage


# Close the connection
