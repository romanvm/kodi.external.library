# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from collections import namedtuple
from pprint import pformat

from libs import simple_requests as requests
from libs.kodi_service import ADDON, logger, get_kodi_url

KODI_URL = get_kodi_url()
TVShowDetails = namedtuple('TVShowDetails', ['title', 'tvdbid'])


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
    logger.debug('JSON-RPC request: %s', request)
    auth = None
    login = ADDON.getSetting('kodi_login')
    password = ADDON.getSetting('kodi_password')
    if login:
        auth = (login, password)
    try:
        json_reply = requests.post(KODI_URL + '/jsonrpc', json=request, auth=auth).json()
    except requests.RequestException as exc:
        raise ConnectionError from exc
    logger.debug('JSON-RPC reply: %s', pformat(json_reply))
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
            'director', 'genre', 'cast', 'art', 'year', 'studio'
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
        'properties': ['plot', 'genre', 'cast', 'art', 'year', 'studio'],
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
        'properties': ['showtitle', 'season', 'tvshowid', 'art'],
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
    :param recent:
    :return:
    """
    params = {
        'properties': [
            'showtitle', 'season', 'episode', 'title', 'tvshowid',
            'cast', 'firstaired', 'director', 'plot', 'file', 'playcount', 'resume', 'art'
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


def update_item_playcount(content, id_, playcount):
    """
    Update item's playcount
    """
    if content.endswith('movies'):
        method = 'VideoLibrary.SetMovieDetails'
        params = {'movieid': id_, 'playcount': playcount}
    else:
        method = 'VideoLibrary.SetEpisodeDetails'
        params = {'episodeid': id_, 'playcount': playcount}
    _send_json_rpc(method, params)
