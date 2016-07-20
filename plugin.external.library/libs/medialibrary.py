# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import requests
from simpleplugin import Plugin

plugin = Plugin()
kodi_url = 'http://{host}:{port}'.format(host=plugin.kodi_host, port=plugin.kodi_port)


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


def get_movies():
    """
    Get the list of movies from the Kodi database

    :return: the list of movie data as Python dicts
    :rtype: list
    :raises NoDataError: if the Kodi library has no movies
    """
    params = {
        'properties': [
            'imdbnumber',
            'playcount',
            'art',
            'title',
            'plot',
            'genre',
            'cast',
            'year'
            ],
        'sort': {'order': 'ascending', 'method': 'label'}
        }
    result = _send_json_rpc('VideoLibrary.GetMovies', params)
    if not result.get('movies'):
        raise NoDataError
    return result['movies']
