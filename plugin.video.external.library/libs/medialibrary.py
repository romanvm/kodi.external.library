# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from collections import namedtuple
import requests
from simpleplugin import Plugin

plugin = Plugin()
kodi_url = 'http://{host}:{port}'.format(host=plugin.kodi_host, port=plugin.kodi_port)
TVShowDetails = namedtuple('TVShowDetails', ['title', 'tvdbid'])


class ConnectionError(Exception):
    pass


class NoDataError(Exception):
    pass


def _send_json_rpc(method, params=None):
    """
    Send JSON-RPC to remote Kodi

    :param method: Kodi JSON-RPC method
    :type method: str
    :param params: method parameters
    :type params: dict
    :return: JSON-RPC response
    :rtype: dict
    """
    request = {'jsonrpc': '2.0', 'method': method, 'id': '1'}
    if params is not None:
        request['params'] = params
    plugin.log('JSON-RPC request: {0}'.format(request))
    try:
        json_reply = requests.post(kodi_url + '/jsonrpc', json=request).json()
    except requests.RequestException:
        raise ConnectionError
    plugin.log('JSON-RPC reply: {0}'.format(json_reply))
    return json_reply['result']


def _get_info(method, params):
    """
    Get the list of media items for Kodi database

    :param method:
    :param additional_properties:
    :param sort:
    :return:
    """
    params['properties'] += ['art']
    return _send_json_rpc(method, params)


def get_movies(recent=False):
    """
    Get the list of movies from the Kodi database

    :param recent:
    :return: the list of movie data as Python dicts
    :rtype: list
    :raises NoDataError: if the Kodi library has no movies
    """
    if recent:
        method = 'VideoLibrary.GetRecentlyAddedMovies'
        sort = {'order': 'descending', 'method': 'dateadded'}
    else:
        method = 'VideoLibrary.GetMovies'
        sort = {'order': 'ascending', 'method': 'label'}
    params = {
        'properties': [
            'file', 'playcount', 'resume', 'plot',
            'director', 'genre', 'cast', 'imdbnumber', 'year', 'studio'
        ],
        'sort': sort
    }
    result = _get_info(method, params)
    if not result.get('movies'):
        raise NoDataError
    return result['movies']


def get_tvshows():
    """
    Get the list ov TV shows from Kodi

    :return:
    """
    method = 'VideoLibrary.GetTVShows'
    params = {
        'properties': ['plot', 'genre', 'cast', 'imdbnumber', 'year', 'studio'],
        'sort': {'order': 'ascending', 'method': 'label'},
    }
    result = _get_info(method, params)
    if not result.get('tvshows'):
        raise NoDataError
    return result['tvshows']


def get_seasons(tvshowid):
    """
    Get the list ot seasons of a TV show

    :param tvshowid:
    :return:
    """
    method = 'VideoLibrary.GetSeasons'
    params = {
        'tvshowid': tvshowid,
        'properties': ['showtitle', 'season', 'tvshowid'],
        'sort': {'order': 'ascending', 'method': 'season'},
    }
    result = _get_info(method, params)
    if not result.get('seasons'):
        raise NoDataError
    return result['seasons']


def get_episodes(tvshowid=-1, season=-1, recent=False):
    """
    Get the list of episodes from Kodi

    :param tvshowid:
    :param season:
    :return:
    """
    params = {
        'properties': [
            'showtitle', 'season', 'episode', 'title', 'tvshowid',
            'cast', 'firstaired', 'director', 'plot', 'file', 'playcount', 'resume'
        ],
    }
    if recent:
        method = 'VideoLibrary.GetRecentlyAddedEpisodes'
        params['sort'] = {'order': 'descending', 'method': 'dateadded'}
    else:
        method = 'VideoLibrary.GetEpisodes'
        params['tvshowid'] = tvshowid
        params['season'] = season
        params['sort'] = {'order': 'ascending', 'method': 'episode'}
    result = _get_info(method, params)
    if not result.get('episodes'):
        raise NoDataError
    return result['episodes']
