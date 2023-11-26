# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urllib.parse import quote, urljoin, parse_qsl, urlencode

import xbmcplugin
from xbmcgui import Dialog, ListItem

from libs import medialibrary
from libs.kodi_service import ADDON, ADDON_ID, GettextEmulator, logger, get_kodi_url
from libs.mem_storage import MemStorage

_ = GettextEmulator.gettext

PLUGIN_URL = f'plugin://{ADDON_ID}/'
HANDLE = int(sys.argv[1])

DIALOG = Dialog()
STORAGE = MemStorage()

KODI_URL = get_kodi_url(with_credentials=True)
IMAGE_URL = urljoin(KODI_URL, 'image')
VIDEO_URL = urljoin(KODI_URL, 'vfs')


def get_url(**kwargs):
    return PLUGIN_URL + '?' + urlencode(kwargs)


def root():
    """Root action"""
    if ADDON.getSettingBool('show_movies'):
        list_item = ListItem(f'[{_("Movies")}]')
        list_item.setArt({'icon': 'DefaultMovies.png', 'thumb': 'DefaultMovies.png'})
        url = get_url(content='movies')
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=True)
    # if ADDON.getSettingBool('show_tvshows'):
    #     list_item = ListItem(f'[{_("TV Shows")}]')
    #     list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': 'DefaultTVShows.png'})
    #     url = get_url(content='tvshows')
    #     xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=True)


def show_movies():
    xbmcplugin.setPluginCategory(HANDLE, _('Movies'))
    xbmcplugin.setContent(HANDLE, 'movies')
    movies = medialibrary.get_movies()
    for mov in movies:
        list_item = ListItem(mov['label'])
        poster = mov.get('art', {}).get('poster', '')
        fanart = mov.get('art', {}).get('fanart', '')
        list_item.setArt({
            'poster': f'{IMAGE_URL}/{quote(poster)}',
            'fanart': f'{IMAGE_URL}/{quote(fanart)}',
        })
        list_item.setInfo('video', {
            'plot': mov.get('plot', ''),
            'year': mov.get('year', -1),
            'genre': mov.get('genre', []),
            'director': mov.get('director', []),
            'studio': mov.get('studio', []),
        })
        url = f'{VIDEO_URL}/{quote(mov["file"])}'
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=False)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    logger.debug('Called addon with params: %s', str(sys.argv))
    if 'content' not in params:
        root()
    xbmcplugin.endOfDirectory(HANDLE)
