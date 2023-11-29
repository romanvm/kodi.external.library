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

from typing import Type, List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, quote

from libs import medialibrary_api
from libs.kodi_service import GettextEmulator, get_remote_kodi_url

_ = GettextEmulator.gettext

REMOTE_KODI_URL = get_remote_kodi_url(with_credentials=True)
VIDEO_URL = urljoin(REMOTE_KODI_URL, 'vfs')


class BaseContentTypeHandler:
    content: str
    mediatype: str
    item_is_folder: bool
    should_save_to_mem_storage: bool
    api_class: Type[medialibrary_api.BaseMediaItemsRetriever]

    def __init__(self, tvshowid: Optional[int] = None,
                 season: Optional[int] = None,
                 parent_category: Optional[str] = None):
        self._tvshowid = tvshowid
        self._season = season
        self._parent_category = parent_category
        self._api = self.api_class(self.content, self._tvshowid, self._season)

    def get_media_items(self) -> List[Dict[str, Any]]:
        return self._api.get_media_items()

    def get_plugin_category(self) -> str:
        raise NotImplementedError

    def get_item_url(self, media_info: Dict[str, Any]) -> str:
        raise NotImplementedError

    def get_item_context_menu(self) -> List[Tuple[str, str]]:
        raise NotImplementedError


class MoviesHandler(BaseContentTypeHandler):
    content = 'movies'
    mediatype = 'movie'
    item_is_folder = False
    should_save_to_mem_storage = True
    api_class = medialibrary_api.GetMovies

    def get_plugin_category(self) -> str:
        return _('Movies')

    def get_item_url(self, media_info):
        return f'{VIDEO_URL}/{quote(media_info["file"])}'


class RecentMoviesHandler(MoviesHandler):
    api_class = medialibrary_api.GetRecentlyAddedMovies

    def get_plugin_category(self) -> str:
        return _('Recently added movies')
