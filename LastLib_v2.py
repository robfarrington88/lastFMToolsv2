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

# Connect to SQLite database (or create it if it doesn't exist)
def connectToDatabase(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    return conn, cursor
def createDatabase():
    conn, cursor=connectToDatabase('lastScrobbles.db')
    


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
add_scrobble('Artist Name', 'Album Title', 'Song Title')

# Close the connection
