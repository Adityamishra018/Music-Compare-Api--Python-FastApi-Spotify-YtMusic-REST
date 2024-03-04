import os
from pprint import pprint
from ytmusicapi import YTMusic
import mysql.connector

class YTDbContext:
    def __init__(self):
        self.__clear_playlists = ("TRUNCATE TABLE ytPlaylists")
        self.__clear_tracks = ("TRUNCATE TABLE ytTracks")
        self.__add_playlist = ("INSERT INTO ytPlaylists (playlist_id,title,tracks_count,description,artwork)"
                             "Values (%(id)s,%(title)s,%(trackCount)s,%(description)s,%(artwork)s)")
        self.__add_tracks = ("INSERT INTO ytTracks (title,duration,artists,album,playlist_id,artwork)"
                             "Values (%(title)s,%(duration)s,%(artists)s,%(album)s,%(playlist_id)s,%(artwork)s)")
        try:
            self.cnx = mysql.connector.connect(user=os.getenv('DBUSER'), password=os.getenv('DBPWD'),
                                host=os.getenv('DBHOST'),database=os.getenv('DBNAME'))
            self.cursor = self.cnx.cursor(dictionary=True)
        except Exception as e:
            print(e)

    def GetPlaylists(self):
        self.cursor.execute("Select * FROM ytPlaylists")
        playLists = []
        for r in self.cursor:
            playLists.append(r)
        return playLists

    def GetPlaylistTracks(self,playListId,**args):
        query = """Select ytt.title, ytt.duration,ytt.artists,ytt.album,ytt.artwork,ytp.title as playlist_title 
                FROM ytPlaylists ytp INNER JOIN ytTracks ytt on ytt.playlist_id = ytp.playlist_id
                WHERE ytp.playlist_id = %s"""
        if 'desc' in args and args['desc']:
            query = query + "Order by id desc"
        self.cursor.execute(query,(playListId,))
        tracks = []
        for r in self.cursor:
            tracks.append(r)
        return tracks
    
    def AddPlaylists(self,playlists):
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cursor.execute(self.__clear_playlists)
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.cursor.executemany(self.__add_playlist,playlists)
        self.cnx.commit()
        return self.cursor.rowcount

    def AddTracks(self,tracks):
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self.cursor.execute(self.__clear_tracks)
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.cursor.executemany(self.__add_tracks,tracks)
        self.cnx.commit()
        return self.cursor.rowcount

    def __del__(self):
        self.cnx.close();

class YTContext(YTMusic):
    def __init__(self,userId,*args):
        super().__init__(*args)
        self.__db = YTDbContext()
        self.__userId = userId
        self.__song_details = ['duration','title','artists','album','playlist_id']
        self.__playlist_details = ['id','trackCount','title','description','thumbnails']
        
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
    
    def importPlaylists(self):
        playlists = self.get_user_playlists(self.__userId,self.get_user(self.__userId)['playlists']['params'])
       
        playlist_details = []
        playlist_tracks = []

        for p in playlists:
            resp = self.get_playlist(playlistId=p['playlistId'])

            playlist_detail = {key : resp[key] for key in self.__playlist_details if key in resp}
            playlist_detail['artwork'] = playlist_detail['thumbnails'][1]['url'];del playlist_detail['thumbnails'];
            playlist_details.append(playlist_detail)

            for t in resp['tracks']:
                entry = {key : ', '.join(artist['name'] for artist in t[key]) if key == 'artists' else t[key] for key in self.__song_details if key in t}
                
                #handle album
                if isinstance(entry['album'],dict):
                    entry['album'] = entry['album']['name']

                #handle missing duration
                if 'duration' not in entry:
                    entry['duration'] = 0
                else:
                    entry['duration'] = self.__duration_to_s(entry['duration'])

                #handle track artwork
                entry['artwork'] = t['thumbnails'][-1]['url']
                
                #attach playlist_id
                entry['playlist_id'] = p['playlistId']
                playlist_tracks.append(entry)

        return {
            "Youtube music playlists added" : self.__db.AddPlaylists(playlist_details),
            "Youtube music tracks added" : self.__db.AddTracks(playlist_tracks)
        }

if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    app = YTContext(os.getenv('YTUSERID'),'oauth.json')
    app.importPlaylists()
