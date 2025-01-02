import os
import requests
import sqlite3
from pprint import pprint
from typing import List, Dict, Any

class SPDbContext:
    def __init__(self):
        self.__clear_playlists = "DELETE FROM spPlaylists"
        self.__clear_tracks = "DELETE FROM spTracks"
        self.__add_playlist = """
            INSERT INTO spPlaylists (playlist_id, title, tracks_count, description, artwork)
            VALUES (:id, :title, :trackCount, :description, :artwork)
        """
        self.__add_tracks = """
            INSERT INTO spTracks (title, duration, artists, album, playlist_id, artwork)
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
        self.cursor.execute("SELECT * FROM spPlaylists")
        return [dict(row) for row in self.cursor.fetchall()]

    def GetPlaylistTracks(self, playListId: str, **args) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                spt.title, 
                spt.duration,
                spt.artists,
                spt.album,
                spt.artwork,
                spp.title as playlist_title 
            FROM spPlaylists spp 
            INNER JOIN spTracks spt ON spp.playlist_id = spt.playlist_id
            WHERE spp.playlist_id = ?
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

class SPContext:
    def __init__(self,userId):
        token_headers = { "Content-Type" : "application/x-www-form-urlencoded"}
        token_data = { "grant_type" : "client_credentials",
                "client_id" : os.getenv('CLIENTID'),
                "client_secret" : os.getenv('SECRET')}
        
        resp = requests.post('https://accounts.spotify.com/api/token',headers=token_headers,data=token_data).json()
        self.headers = {'Authorization' : f"Bearer {resp['access_token']}"}
        self.userId = userId
        self.CheckConnection()
        self.__db = SPDbContext() 
    
    def importPlaylists(self):
        playlists = self.getPlaylists()
        p_count = self.__db.AddPlaylists(playlists)
        all_tracks = []
        for p in playlists:
            tracks = self.getPlaylistTracks(p['id'])
            all_tracks.extend(tracks)
        t_count = self.__db.AddTracks(all_tracks)

        return {
            "Spotify playlists added" : p_count,
            "Spotify tracks added" : t_count
        }

    def CheckConnection(self):
        resp = requests.get(f"https://api.spotify.com/v1/users/{self.userId}",headers=self.headers).json()
        if 'error' not in resp:
            print('Connection established')
    
    def getPlaylistTracks(self,playListId):
        tracks = []
        next = f"https://api.spotify.com/v1/playlists/{playListId}/tracks"
        while True:
            resp = requests.get(next,headers=self.headers).json()
            next = resp['next']
            for i in resp['items']:
                if i['track'] is not None:
                    try:
                        tracks.append({
                            'title' : i['track']['name'],
                            'album' : i['track']['album']['name'],
                            'artists' : ', '.join(artist['name'] for artist in i['track']['artists'] if artist['name'] is not None),
                            'duration' : i['track']['duration_ms']//1000,
                            'playlist_id' : playListId,
                            'artwork' : i['track']['album']['images'][1]['url']
                        })
                    except Exception as e:
                        pprint(i['track'])
            if next is None:
                break
        return tracks
    
    def getDbPlaylistTracks(self,playlistId):
        return self.__db.GetPlaylistTracks(playlistId)
    
    def getDbAllTracks(self):
        playlists = self.__db.GetPlaylists()
        tracks = []
        for p in playlists:
            tracks.extend(self.__db.GetPlaylistTracks(p['playlist_id']))
        return tracks
    
    def getPlaylists(self):
        resp = requests.get(f"https://api.spotify.com/v1/users/{self.userId}/playlists",headers=self.headers).json()
        playlist_details = []
        for i in resp['items']:
            item = {
                'title' : i['name'],
                'trackCount' : i['tracks']['total'],
                'id' : i['id'],
                'description' : i['description'],
                'artwork' : i['images'][1]['url']
            }
            playlist_details.append(item)
        return playlist_details
    
    def getDbPlaylists(self):
        return self.__db.GetPlaylists()
        
if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    app = SPContext(os.getenv('SPUSERID'))
    pprint(app.importPlaylists())