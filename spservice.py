import os
import requests
import mysql.connector
from pprint import pprint

class SPDbContext:
    def __init__(self):
        self.__clear_playlists = ("TRUNCATE TABLE spPlaylists")
        self.__clear_tracks = ("TRUNCATE TABLE spTracks")
        self.__add_playlist = ("INSERT INTO spPlaylists (playlist_id,title,tracks_count,description,artwork)"
                             "Values (%(id)s,%(title)s,%(trackCount)s,%(description)s,%(artwork)s)")
        self.__add_tracks = ("INSERT INTO spTracks (title,duration,artists,album,playlist_id,artwork)"
                             "Values (%(title)s,%(duration)s,%(artists)s,%(album)s,%(playlist_id)s,%(artwork)s)")
        try:
            self.cnx = mysql.connector.connect(user=os.getenv('DBUSER'), password=os.getenv('DBPWD'),host=os.getenv('DBHOST'),database=os.getenv('DBNAME'))
            self.cursor = self.cnx.cursor(dictionary=True)
        except Exception as e:
            print(e)

    def GetPlaylists(self):
        self.cursor.execute("Select * FROM spPlaylists")
        playLists = []
        for r in self.cursor:
            playLists.append(r)
        return playLists

    def GetPlaylistTracks(self,playListId,**args):
        query = """Select spt.title, spt.duration,spt.artists,spt.album,spt.artwork,spp.title as playlist_title 
                FROM spPlaylists spp INNER JOIN spTracks spt on spp.playlist_id = spt.playlist_id
                WHERE spp.playlist_id = %s"""
                
        if 'desc' in args and args['desc']:
            query = query + "Order by id desc"
        self.cursor.execute(query,(playListId,))
        tracks = []
        for r in self.cursor:
            tracks.append(r)
        return tracks

    def AddPlaylists(self,playlists) -> int:
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cursor.execute(self.__clear_playlists)
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.cursor.executemany(self.__add_playlist,playlists)
        self.cnx.commit()
        return self.cursor.rowcount

    def AddTracks(self,tracks) -> int:
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cursor.execute(self.__clear_tracks)
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.cursor.executemany(self.__add_tracks,tracks)
        self.cnx.commit()
        return self.cursor.rowcount

    def __del__(self):
        self.cnx.close();

class SPContext:
    def __init__(self,userId):
        token_headers = { "Content-Type" : "application/x-www-form-urlencoded"}
        token_data = { "grant_type" : "client_credentials",
                "client_id" : os.getenv('CLIENTID'),
                "client_secret" : os.getenv('SECRET')}
        
        resp = requests.post('https://accounts.spotify.com/api/token',headers=token_headers,data=token_data).json()
        print(resp['access_token'])
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
                    tracks.append({
                        'title' : i['track']['name'],
                        'album' : i['track']['album']['name'],
                        'artists' : ', '.join(artist['name'] for artist in i['track']['artists']),
                        'duration' : i['track']['duration_ms']//1000,
                        'playlist_id' : playListId,
                        'artwork' : i['track']['album']['images'][1]['url']
                    })
            if next is None:
                break;
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
    app.importPlaylists()