#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import urllib.parse
import urllib.request
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

# Constantes
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_FANART = ADDON.getAddonInfo('fanart')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_PROFILE = ADDON.getAddonInfo('profile')
ADDON_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
HANDLE = int(sys.argv[1])

# URLs
BASE_URL = sys.argv[0]

def build_url(query):
    return BASE_URL + '?' + urllib.parse.urlencode(query)

def get_params():
    param_string = sys.argv[2]
    if len(param_string) >= 2:
        params = dict(urllib.parse.parse_qsl(param_string[1:]))
    else:
        params = {}
    return params

def fetch_trakt_data(url, params=None):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(ADDON_SETTINGS.getSetting('trakt_access_token'))
    }
    data = None
    if params:
        data = json.dumps(params).encode('utf-8')
    request = urllib.request.Request(url, data=data, headers=headers)
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))

def list_trakt_lists():
    url = 'https://api.trakt.tv/users/me/lists'
    trakt_lists = fetch_trakt_data(url)
    for trakt_list in trakt_lists:
        list_name = trakt_list['name']
        list_url = build_url({'mode': 'show_trakt_list', 'list_id': trakt_list['ids']['trakt']})
        li = xbmcgui.ListItem(label=list_name)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=list_url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def show_trakt_list(list_id):
    url = 'https://api.trakt.tv/users/me/lists/{}/items'.format(list_id)
    items = fetch_trakt_data(url)
    for item in items:
        if item['type'] == 'movie':
            movie = item['movie']
            movie_name = movie['title']
            movie_url = 'plugin://plugin.video.example/?action=play&movie_id={}'.format(movie['ids']['trakt'])
            li = xbmcgui.ListItem(label=movie_name)
            xbmcplugin.addDirectoryItem(handle=HANDLE, url=movie_url, listitem=li, isFolder=False)
        elif item['type'] == 'show':
            show = item['show']
            show_name = show['title']
            show_url = 'plugin://plugin.video.example/?action=play&show_id={}'.format(show['ids']['trakt'])
            li = xbmcgui.ListItem(label=show_name)
            xbmcplugin.addDirectoryItem(handle=HANDLE, url=show_url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def play_movie(movie_id):
    url = 'https://api.trakt.tv/movies/{}/translations'.format(movie_id)
    translations = fetch_trakt_data(url)
    movie_url = translations[0]['title'] # Ejemplo de URL de streaming
    play_item = xbmcgui.ListItem(path=movie_url)
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)

def router(paramstring):
    params = get_params()
    if params:
        if params['mode'] == 'list_trakt_lists':
            list_trakt_lists()
        elif params['mode'] == 'show_trakt_list':
            show_trakt_list(params['list_id'])
        elif params['mode'] == 'play':
            if 'movie_id' in params:
                play_movie(params['movie_id'])
            elif 'show_id' in params:
                play_show(params['show_id'])
    else:
        list_trakt_lists()

if __name__ == '__main__':
    router(sys.argv[2][1:])
