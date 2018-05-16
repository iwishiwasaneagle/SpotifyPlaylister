#!/usr/bin/python
# -*- coding: utf-8 -*-
import spotipy.util as util
import requests
import time
import json
import os
import logging
import urllib
import subprocess
import keys

logging.basicConfig(filename='SpotiPi_activity.log', level=logging.INFO, format='%(asctime)s %(message)s')
username = 'iwishiwasaneagle'
scope = 'playlist-modify-private playlist-modify-public user-library-read user-read-playback-state user-read-currently-playing'

client_id = keys.SPOTIPI_CLIENT_ID
client_secret = keys.SPOTIPI_CLIENT_SECRET
redirect_url = keys.SPOTIPI_REDIRECT_URL
token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret,
                                   redirect_uri=redirect_url)

current = 'https://api.spotify.com/v1/me/player/currently-playing'
playlists = 'https://api.spotify.com/v1/users/{usrname}/playlists'.format(usrname=username)
headers = {"Authorization": 'Bearer ' + str(token)}

current = requests.get(current, headers=headers)
if len(current.text) == 0:
    raise Exception("There is nothing currently playing")
else:
    current = current.json()
playlist = requests.get(playlists, headers=headers).json()

current_song_uri = current["item"]["uri"]
current_song_img = current["item"]["album"]["images"][2]["url"]
current_song_name = current["item"]["name"]
current_song_album = current['item']['album']['name']
current_song_album_uri = current['item']['album']['uri']
current_song_artist = current["item"]["artists"][0]["name"]
monthly_playlist_name = str(
    time.strftime("%B%y"))  # %B Locale’s full month name. %y Year without century as a decimal number [00,99].

cacheName = "cache"
if not os.path.isdir(cacheName):
    os.makedirs(cacheName)
    logging.info("{cacheName} created".format(cacheName=cacheName))

filename_base = current_song_album_uri.split(':')[2]
filename_album_art_png = os.path.join(os.getcwd(), cacheName, filename_base + '.png')
if not os.path.isfile(filename_album_art_png):
    urllib.request.urlretrieve(current_song_img, filename_album_art_png)

found = False
for item in playlist["items"]:
    if item["name"] == monthly_playlist_name:
        monthly_playlist_uri = item["uri"].split(":")[4]
        found = True

if not found:
    # create_playlist
    create_payload = {"name": monthly_playlist_name,
                      "description": "Monthly playlist with my current favourite songs. Created with https://github.com/iwishiwasaneagle/Spotipi",
                      "public": "true"}

    create_url = 'https://api.spotify.com/v1/users/{usrname}/playlists/'.format(usrname=username)
    create = requests.post(create_url, headers=headers, data=json.dumps(create_payload))
    monthly_playlist_uri = create.json()["uri"].split(":")[4]
    logging.info("Created playlist '{playlistName}'".format(playlistName=monthly_playlist_name))

songs = "https://api.spotify.com/v1/users/{usrname}/playlists/{playlist}/tracks".format(usrname=username,
                                                                                      playlist=monthly_playlist_uri)

exists = False
if found:
    monthly_playlist_songs = requests.get(songs, headers=headers).json()

    for item in monthly_playlist_songs['items']:
        if current_song_uri == item['track']['uri']:
            exists = True

if not exists:
    addSongtoPlaylist = 'https://api.spotify.com/v1/users/{username}/playlists/{monthly_playlist_uri}/tracks?uris={current_song_uri}'.format(
        username=username, monthly_playlist_uri=monthly_playlist_uri, current_song_uri=current_song_uri)
    try:
        requests.post(addSongtoPlaylist, headers=headers)
        logging.info("Added song \"{song}\" ({uri}) to {playlist}'".format(song=current_song_name, uri=current_song_uri,
                                                                           playlist=monthly_playlist_name))
        notif_payload = ["Added song to {playlist}".format(playlist=monthly_playlist_name),
                         "{song} - {artist}".format(song=current_song_name, artist=current_song_artist), '-i',
                         filename_album_art_png]

    except:
        logging.error(
            "Failed to add song {song} ({uri}) to {playlist}'".format(song=current_song_name, uri=current_song_uri,
                                                                      playlist=monthly_playlist_name))

        notif_payload = ["Failed to add song to {playlist}".format(playlist=monthly_playlist_name),
                         "{song} - {artist}".format(song=current_song_name, artist=current_song_artist), '-i',
                         filename_album_art_png]

else:
    logging.info(
        "Duplicate detected: song {song} ({uri}) in {playlist}".format(song=current_song_name, uri=current_song_uri,
                                                                       playlist=monthly_playlist_name))
    notif_payload = ["Duplicate addition detected in {playlist}".format(playlist=monthly_playlist_name),
                     "\"{song} - {artist}\" already exists".format(song=current_song_name, artist=current_song_artist),
                     '-i', filename_album_art_png]

notif_payload.insert(0, "notify-send")
subprocess.call(notif_payload)
