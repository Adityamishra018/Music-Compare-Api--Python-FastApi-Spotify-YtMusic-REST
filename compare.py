import os
from dotenv import load_dotenv
from pprint import pprint

from ytservice import YTDbContext
from spservice import SPDbContext
from fuzzywuzzy import fuzz

load_dotenv()

class CompareApp:
    def __init__(self):
        self.__yt = YTDbContext()
        self.__sp = SPDbContext()
        self.ytTracks = []
        self.spTracks = []
        self.threshold = 60

    def GetYtTracksByPlaylistId(self,playlistId,**args):
        tracks = self.__yt.GetPlaylistTracks(playlistId,**args)
        return tracks
    
    def GetSpTracksByPlaylistId(self,playlistId,**args):
        tracks = self.__sp.GetPlaylistTracks(playlistId,**args)
        return tracks
    
    def Compare(self,ytPlaylistId,spPlaylistId,**args):
        self.ytTracks = self.GetYtTracksByPlaylistId(ytPlaylistId,**args)
        self.spTracks = self.GetSpTracksByPlaylistId(spPlaylistId,**args)

        i = j = 0
        out_of_order = []
        missing_in_yt = []
        missing_in_sp = []
        while i < len(self.ytTracks) and j < len(self.spTracks):
            idx = self.GetSimilarityIndex(self.ytTracks[i],self.spTracks[j])
            if idx >= self.threshold:
                i = i + 1
                j = j + 1
            else:
                foundInSp = self.FindInSpotify(i)
                foundInYt = self.FindInYt(j)
                if foundInSp and foundInYt:
                    out_of_order.append(f"{self.ytTracks[i]['title']} ({self.ytTracks[i]['artists']})")
                    i = i+1 
                    j = j+1
                elif foundInSp:
                    missing_in_yt.append(f"{self.spTracks[j]['title']} ({self.spTracks[j]['artists']})")
                    j = j+1
                else:
                    missing_in_sp.append(f"{self.ytTracks[i]['title']} ({self.ytTracks[i]['artists']})")
                    i = i+1
                    
        return {
            "ytMusic track count" : len(self.ytTracks),
            "spotify track count" : len(self.spTracks),
            "missing in Spotify" : missing_in_sp if len(missing_in_sp) > 0 else None,
            "missing in Youtube" : missing_in_yt if len(missing_in_yt) > 0 else None,
            "out of order" : out_of_order if len(out_of_order) > 0 else None
        }
    
    def FindInSpotify(self,ytIdx):
        for t in self.spTracks:
            if self.GetSimilarityIndex(self.ytTracks[ytIdx],t) >= self.threshold:
                return True
        return False
    
    def FindInYt(self,spIdx):
        for t in self.ytTracks:
            if self.GetSimilarityIndex(t,self.spTracks[spIdx]) >= self.threshold:
                return True
        return False


    def GetSimilarityIndex(self,ytTrack,spTrack):
        name_ratio = fuzz.partial_ratio(ytTrack['title'].lower(),spTrack['title'].lower())
        artist_ratio = fuzz.partial_ratio(ytTrack['artists'].lower(),spTrack['artists'].lower())
        album_ratio = fuzz.partial_ratio(ytTrack['album'],spTrack['album'])
        if album_ratio != 0:
            avg = (name_ratio + artist_ratio*2 + album_ratio) / 4
        else:
            avg = (name_ratio + artist_ratio*2 ) / 3
        duration_diff = ytTrack['duration']- spTrack['duration']
        if abs(duration_diff) <= 3:
            avg += 10
        return avg





