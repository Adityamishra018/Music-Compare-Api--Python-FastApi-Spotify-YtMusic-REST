import os
import sqlite3
from pprint import pprint
from typing import Any, Dict, List
from dotenv import load_dotenv
from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

CLIENT_SECRETS_FILE = 'client_secret.json'

DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')
SCOPES = ['https://www.googleapis.com/auth/youtube']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

class YTDbContext:
    def __init__(self):
        self.__clear_playlists = "DELETE FROM ytPlaylists"
        self.__clear_tracks = "DELETE FROM ytTracks"
        self.__add_playlist = """
            INSERT INTO ytPlaylists (playlist_id, title, tracks_count, description, artwork)
            VALUES (:id, :title, :trackCount, :description, :artwork)
        """
        self.__add_tracks = """
            INSERT INTO ytTracks (title, duration, artists, album, playlist_id, artwork)
            VALUES (:title, :duration, :artists, :album, :playlist_id, :artwork)
        """
        
        try:
            self.cnx = sqlite3.connect('.\playlists.db')
            self.cnx.execute("PRAGMA foreign_keys = ON")
            self.cnx.row_factory = sqlite3.Row
            self.cursor = self.cnx.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def GetPlaylists(self) -> List[Dict[str, Any]]:
        self.cursor.execute("SELECT * FROM ytPlaylists")
        return [dict(row) for row in self.cursor.fetchall()]

    def GetPlaylistTracks(self, playListId: str, **args) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                ytt.title, 
                ytt.duration,
                ytt.artists,
                ytt.album,
                ytt.artwork,
                ytp.title as playlist_title 
            FROM ytPlaylists ytp 
            INNER JOIN ytTracks ytt ON ytt.playlist_id = ytp.playlist_id
            WHERE ytp.playlist_id = ?
        """
        if 'desc' in args and args['desc']:
            query += " ORDER BY id DESC"
        
        self.cursor.execute(query, (playListId,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def AddPlaylists(self, playlists: List[Dict[str, Any]]) -> int:
        with self.cnx: # This creates a transaction
            self.cursor.execute(self.__clear_playlists)
            self.cursor.executemany(self.__add_playlist, playlists)
            return self.cursor.rowcount

    def AddTracks(self, tracks: List[Dict[str, Any]]) -> int:
        with self.cnx: # This creates a transaction
            self.cursor.execute(self.__clear_tracks)
            self.cursor.executemany(self.__add_tracks, tracks)
            return self.cursor.rowcount

    def __del__(self):
        if hasattr(self, 'cnx'):
            self.cnx.close()

class YTContext():
    def __init__(self,userId):
        # flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        # credentials = flow.run_local_server()
        # self.__client = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        #                         credentials=credentials)

        self.__client = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                 developerKey=DEVELOPER_KEY)
        self.__db = YTDbContext()
        self.__userId = userId
        
    def __duration_to_s(self,duration):
        hrs = minutes = seconds = 0
        if len(duration.split(":")) ==2:
            minutes, seconds = duration.split(":")
        elif len(duration.split(":")) == 3:
            hrs, minutes, seconds = duration.split(":")
        else:
            return 0
        return int(hrs)*3600 + int(minutes)*60 + int(seconds)

    def GetPlaylists(self):
        return self.__db.GetPlaylists()
    
    def GetPlaylistTracks(self,playlistId):
        return self.__db.GetPlaylistTracks(playlistId)
    
    def GetAllTracks(self):
        playlists = self.__db.GetPlaylists()
        tracks = []
        for p in playlists:
            tracks.extend(self.__db.GetPlaylistTracks(p['playlist_id']))
        return tracks
    
    def getPlaylistItems(self,playListId, nextPageToken = None):
        return self.__client.playlistItems().list(
                    part="snippet",
                    playlistId=playListId,
                    maxResults = 50,
                    pageToken = nextPageToken).execute()
    
    def importPlaylists(self):
        playlists = self.__client.playlists().list(
            part='snippet,contentDetails',
            channelId = self.__userId,
            maxResults=20
        ).execute()['items']
       
        playlist_details = []
        playlist_tracks = []

        for p in playlists:
            playlist_detail = {
                'id' : p['id'],
                'trackCount' : p['contentDetails']['itemCount'],
                'title' : p['snippet']['title'],
                'description': p['snippet']['description'] ,
                'artwork' : p['snippet']['thumbnails']['medium']['url']
            }

            playlist_details.append(playlist_detail)

            resp = self.getPlaylistItems(p['id'])
            while True:
                for t in resp['items']:
                    try:
                        entry = {
                            'title' : t['snippet']['title'],
                            'duration' : 0,
                            'artwork' : t['snippet']['thumbnails']['default']['url'],
                            'playlist_id' : p['id']
                        }
                    except Exception:
                        pass

                    try:
                        entry['album'] = t['snippet']['description'].split('\n')[4][:90]
                    except Exception:
                        entry['album'] = ''
                        
                    try:
                        entry['artists'] = t['snippet']['description'].split('\n')[2][:140]
                    except Exception:
                        entry['artists'] = ''
                
                    playlist_tracks.append(entry)

                if resp.get('nextPageToken'):
                    resp = self.getPlaylistItems(p['id'],resp['nextPageToken'])
                else:
                    break
        return {
            "Youtube music playlists added" : self.__db.AddPlaylists(playlist_details),
            "Youtube music tracks added" : self.__db.AddTracks(playlist_tracks)
        }
    
if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    app = YTContext(os.getenv('YTUSERID'))
    pprint(app.importPlaylists())
