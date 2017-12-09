#!/usr/bin/python
# -*- coding: utf-8 -*-
import spotipy.util as util
import requests, time, json, os, logging

logging.basicConfig(filename='SpotiPi_activity.log', level=logging.INFO, format='%(asctime)s %(message)s')

username = 'iwishiwasaneagle'
scope = 'playlist-modify-private playlist-modify-public user-library-read user-read-playback-state user-read-currently-playing'
client_id = os.environ['SPOTIPI_CLIENT_ID']
client_secret = os.environ['SPOTIPI_CLIENT_SECRET']
redirect_url = os.environ['SPOTIPI_REDIRECT_URL']
token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_url)

current='https://api.spotify.com/v1/me/player/currently-playing'
playlists = 'https://api.spotify.com/v1/users/'+username+'/playlists'
headers = {"Authorization" :  'Bearer '+str(token)}
current = requests.get(current, headers=headers).json()
playlist = requests.get(playlists, headers=headers).json()

current_song_uri = current["item"]["uri"]
current_song_name = current["item"]["name"]
monthly_playlist_name = str(time.strftime("%B%y")) #%B Locale’s full month name. %y Year without century as a decimal number [00,99].


found = False
for item in playlist["items"]:
    if item["name"] == monthly_playlist_name:
        monthly_playlist_uri = item["uri"].split(":")[4]
        found = True

if not found:
    #create_playlist
    create_payload = {"name": monthly_playlist_name,
                        "description":"Monthly playlist with my current favourite songs",
                        "public":"true"}
    create_url = 'https://api.spotify.com/v1/users/'+username+'/playlists/'
    create = requests.post(create_url, headers=headers, data=json.dumps(create_payload))
    monthly_playlist_uri = create.json()["uri"].split(":")[4]
    logging.info("Created playlist %s"%(monthly_playlist_name))

addSongtoPlaylist = 'https://api.spotify.com/v1/users/'+username+'/playlists/'+monthly_playlist_uri+'/tracks?uris='+current_song_uri
logging.info("Added song %s (%s) to %s"%(current_song_name, current_song_uri, monthly_playlist_name))
requests.post(addSongtoPlaylist, headers=headers)
