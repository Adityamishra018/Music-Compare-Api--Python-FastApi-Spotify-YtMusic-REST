import os
from dotenv import load_dotenv
from ytservice import YTContext
from spservice import SPContext

load_dotenv()

class ImportMusic:
    def __init__(self):
        self.__yt = YTContext(os.getenv('YTUSERID'),'oauth.json')
        self.__sp = SPContext(os.getenv('SPUSERID'))

    def UpdateYTDb(self):
        self.__yt.importPlaylists()

    def UpdateSPDb(self):
        self.__sp.importPlaylists()

app = ImportMusic()
app.UpdateSPDb()
# app.UpdateYTDb()