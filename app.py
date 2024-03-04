import os
from fastapi import FastAPI, Query
from typing import Literal, Optional
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from compare import CompareApp
from ytservice import YTContext
from spservice import SPContext

load_dotenv()

server = FastAPI(title="Compare Playlists and Search")

server.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=["GET", "POST"],
    allow_headers=["*"])

app = CompareApp()
ytService = YTContext(os.getenv('YTUSERID'),'oauth.json')
spService = SPContext(os.getenv('SPUSERID'))

@server.get('/api/compare', tags=['Compare'])
def compare(ytId: str, spId: str):
    resp = app.Compare(ytId,spId)
    return resp

@server.get('/api/playlists/{name}', tags=['Lookup'])
def get_playlist(name : Literal['sp','yt']):
    if name == 'yt':
        return ytService.GetPlaylists()
    return spService.getDbPlaylists()

@server.get('/api/tracks/{name}', tags=['Lookup'])
def get_tracks(name : Literal['sp','yt'], id : Optional[str] = None):
    if name == 'yt':
        if id:
            return ytService.GetPlaylistTracks(id)
        else:
            return ytService.GetAllTracks()
    elif name == 'sp':
        if id:
            return spService.getDbPlaylistTracks(id)
        else:
            return spService.getDbAllTracks()

@server.post('/api/sync', tags=['Sync'])
def update(name : Optional[Literal['yt','sp']] = Query(default=None,description="you can provide either sp or yt as name")):
    if name == 'yt':
        return ytService.importPlaylists()
    elif name == 'sp':
        return spService.importPlaylists()
    elif name == None:
        ytres= ytService.importPlaylists()
        spres= spService.importPlaylists()
        return {
            **ytres,**spres
        }

