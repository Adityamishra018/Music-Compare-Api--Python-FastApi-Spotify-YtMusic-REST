## Music Compare Api

## About the project

This project creates an api for users to compare their ytmusic and spotify playlists and find out tracks missing in either of them or the tracks that are not in order.

## Concepts covered

1. REST API
2. Python FastApi
3. MySQL
4. Oauth integration
5. Auth Token integration

## How to use ?

1. Clone repo
2. Install MySQL (consider [MariaDb](https://mariadb.org/))
3. Run the given sql script in project to set-up required tables.
4. Get Spotify ClientId and Secret token from [Spotify](https://developer.spotify.com/documentation/web-api/concepts/access-token)
5. Install ytmusicapi lib with `pip install ytmusicapi`
6. Run `ytmusicapi oauth` at root level and login with your credentials, this will generate OAuth.json file in the root folder which will be referenced by the app.
7. Now we have everything to create .env file for our project which is mandatory for application to run properly.
8. Create .env file at root level of project and add following entries, *I have given example values*
   ```
   YTUSERID=dada******adnaA
   SPUSERID=1**************i6ry
   DBUSER=root
   DBPWD=root
   DBHOST=127.0.0.1
   DBNAME=music_sync
   CLIENTID=883*******************fcf
   SECRET=c58******************8dca
   ```
9. Run `pip install fastapi uvicorn` to install deps.
10. Run `uvicorn app:server` to start the server at host 8000.
11. Open localhost:8000/docs in your browser to work with swagger interface

## Snaps

![swagger](https://drive.google.com/uc?export=view&id=1ekuUxm6fJsupaX9kTxBYMa-9kk9HDiL4)
  
