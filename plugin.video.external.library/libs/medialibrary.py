# Copyright (C) 2023, Roman Miroshnychenko aka Roman V.M.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pprint import pformat
from typing import List, Dict, Any

from libs import simple_requests as requests
from libs.kodi_service import ADDON, logger, get_kodi_url


class NoDataError(Exception):
    pass


class BaseJsonRpcApi:
    kodi_url = get_kodi_url()
    method = None

    def send_json_rpc(self):
        """
        Send JSON-RPC to remote Kodi
        """
        request = {
            'jsonrpc': '2.0',
            'method': self.method,
            'params': self.get_params(),
            'id': '1',
        }
        logger.debug('JSON-RPC request: %s', pformat(request))
        auth = None
        login = ADDON.getSetting('kodi_login')
        password = ADDON.getSetting('kodi_password')
        if login:
            auth = (login, password)
        try:
            json_reply = requests.post(self.kodi_url + '/jsonrpc', json=request, auth=auth).json()
        except requests.RequestException as exc:
            raise ConnectionError from exc
        logger.debug('JSON-RPC reply: %s', pformat(json_reply))
        return json_reply

    def get_params(self):
        """Get params to send to Kodi JSON-RPC API"""
        raise NotImplementedError


class BaseMediaItemsRetriever(BaseJsonRpcApi):
    content = None
    properties = None
    sort = None
    tvshowid = None
    season = None

    def get_params(self):
        params = {
            'properties': self.properties,
            'sort': self.sort,
        }
        if self.tvshowid is not None:
            params['tvshowid'] = self.tvshowid
        if self.season is not None:
            params['season'] = self.season
        return params

    def get_media_items(self) -> List[Dict[str, Any]]:
        """
        Get the list of media items for Kodi database
        """
        try:
            return self.send_json_rpc()['result'][self.content]
        except KeyError as exc:
            raise NoDataError(f'Unable to retrieve {self.content} from remote media library') from exc


class Movies(BaseMediaItemsRetriever):
    method = 'VideoLibrary.GetMovies'
    properties = [
        'file',
        'playcount',
        'resume',
        'plot',
        'director',
        'genre',
        'cast',
        'year',
        'studio',
        'country',
        'title',
        'writer',
        'premiered',
        'mpaa',
        'ratings',
        'art',
    ]
    sort = {'order': 'ascending', 'method': 'label'}


class RecentMovies(Movies):
    method = 'VideoLibrary.GetRecentlyAddedMovies'
    sort = {'order': 'descending', 'method': 'dateadded'}


class TvShows(BaseMediaItemsRetriever):
    method = 'VideoLibrary.GetTVShows'
    properties = [
        'plot',
        'genre',
        'cast',
        'year',
        'studio',
        'art',
    ]
    sort = {'order': 'ascending', 'method': 'label'}


class Seasons(BaseMediaItemsRetriever):
    method = 'VideoLibrary.GetSeasons'
    properties = [
        'showtitle',
        'season',
        'tvshowid',
        'art',
    ]
    sort = {'order': 'ascending', 'method': 'season'}


class Episodes(BaseMediaItemsRetriever):
    method = 'VideoLibrary.GetEpisodes'
    properties = [
        'showtitle',
        'season',
        'episode',
        'title',
        'tvshowid',
        'cast',
        'firstaired',
        'director',
        'plot',
        'file',
        'playcount',
        'resume',
        'art',
    ]
    sort = {'order': 'ascending', 'method': 'label'}


class RecentEpisodes(Episodes):
    method = 'VideoLibrary.GetRecentlyAddedEpisodes'
    sort = {'order': 'descending', 'method': 'dateadded'}


class BasePlaycountUpdater(BaseJsonRpcApi):

   def __init__(self):
       super().__init__()
       self.playcount = None


def update_item_playcount(content, id_, playcount):
    """
    Update item's playcount
    """
    return
    if content.endswith('movies'):
        method = 'VideoLibrary.SetMovieDetails'
        params = {'movieid': id_, 'playcount': playcount}
    else:
        method = 'VideoLibrary.SetEpisodeDetails'
        params = {'episodeid': id_, 'playcount': playcount}
    _send_json_rpc(method, params)
