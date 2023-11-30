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

from urllib.parse import quote

import xbmc

from libs import json_rpc_api
from libs.kodi_service import logger, ADDON
from libs.mem_storage import MemStorage


class PlayMonitor(xbmc.Player):
    """
    Monitors playback status and updates watches status
    for an episode or a movie from an external library
    """
    def __init__(self):
        super().__init__()
        self._mem_storage = MemStorage()
        self._clear_state()

    def _clear_state(self):
        self.is_monitoring = False
        self._current_time = -1
        self._total_time = -1
        self._playing_file = None
        self._item_info = None

    def onPlayBackStarted(self):
        self._playing_file = self.getPlayingFile()
        self._item_info = self._get_item_info()
        if self._item_info is None:
            self._clear_state()
            return
        self.is_monitoring = True
        try:
            self._total_time = self.getTotalTime()
        except Exception:
            self._total_time = -1
        logger.debug('Started monitoring %s', self._playing_file)

    def onPlayBackStopped(self):
        self._update_watched()

    def onPlayBackEnded(self):
        self._update_watched()

    def onPlayBackPaused(self):
        self._update_watched()

    def update_time(self):
        try:
            self._current_time = self.getTime()
        except Exception:
            self._current_time = -1
        if self._total_time == -1:
            try:
                self._total_time = self.getTotalTime()
            except Exception:
                self._total_time = -1

    def _get_item_info(self):
        if listing := self._mem_storage.get('__external_library_list__'):
            files_on_shares = ADDON.getSettingBool('files_on_shares')
            for item in listing:
                if files_on_shares and item['file'] == self._playing_file:
                    return item
                if quote(item['file']) in self._playing_file:
                    return item
        return None

    def _update_watched(self):
        self.is_monitoring = False
        if (self._current_time != -1 and self._total_time != -1 and
                (self._current_time / self._total_time) >= ADDON.getSettingInt('watched_threshold')):
            try:
                content, id_ = self._get_item_info()
            except RuntimeError:
                logger.error('Unable to update watched status')
            else:
                logger.debug('Updating watched status for %s %s', content[:-1], self._playing_file)
                medialibrary.update_item_playcount(content, id_, 1)
        self._playing_file = None
