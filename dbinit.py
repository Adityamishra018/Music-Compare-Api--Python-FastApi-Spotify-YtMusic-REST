import sqlite3
import os

def create_database(db_name='playlists.db'):
    if os.path.exists(db_name):
        os.remove(db_name)
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    schema = '''
    DROP TABLE IF EXISTS ytTracks;
    DROP TABLE IF EXISTS ytPlaylists;
    DROP TABLE IF EXISTS spTracks;
    DROP TABLE IF EXISTS spPlaylists;

    CREATE TABLE ytPlaylists(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id TEXT UNIQUE,
        title TEXT NOT NULL,
        tracks_count INTEGER,
        description TEXT,
        artwork TEXT
    );

    CREATE TABLE ytTracks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        duration INTEGER,
        artists TEXT NOT NULL,
        album TEXT,
        playlist_id TEXT NOT NULL,
        artwork TEXT,
        FOREIGN KEY (playlist_id) REFERENCES ytPlaylists(playlist_id)
    );

    CREATE TABLE spPlaylists(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id TEXT UNIQUE,
        title TEXT NOT NULL,
        tracks_count INTEGER,
        description TEXT,
        artwork TEXT
    );

    CREATE TABLE spTracks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        duration INTEGER,
        artists TEXT NOT NULL,
        album TEXT,
        playlist_id TEXT NOT NULL,
        artwork TEXT,
        FOREIGN KEY (playlist_id) REFERENCES spPlaylists(playlist_id)
    );
    '''
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    
    print(f"Database '{db_name}' created successfully!")

if __name__ == "__main__":
    create_database()