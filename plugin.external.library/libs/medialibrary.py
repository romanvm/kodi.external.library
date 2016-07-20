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


def send_json_rpc(method, params=None):
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
