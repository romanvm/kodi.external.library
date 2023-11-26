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

from libs import medialibrary as ml
from libs.kodi_service import logger, ADDON
from libs.mem_storage import MemStorage


class PlayMonitor(xbmc.Player):
    """
    Monitors playback status and updates watches status
    for an episode or a movie from an external library
    """
    def __init__(self):
        super().__init__()
        self._storage = MemStorage()
        self.is_monitoring = False
        self._current_time = -1
        self._total_time = -1
        self._playing_file = None
        self._listing = None

    def onPlayBackStarted(self):
        if ml.KODI_URL in self.getPlayingFile():
            self._playing_file = self.getPlayingFile()
            self.is_monitoring = True
            self._listing = self._storage['__external_library_list__']
            logger.debug('Started monitoring %s', self._playing_file)
            try:
                self._total_time = self.getTotalTime()
            except Exception:
                self._total_time = -1

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
        for item in self._listing:
            if quote(item['file']) in self._playing_file:
                if 'movieid' in item:
                    content = 'movies'
                    id_ = item['movieid']
                else:
                    content = 'episodes'
                    id_ = item['episodeid']
                return content, id_
        raise RuntimeError('Played item {0} is not in listing!'.format(self._playing_file))

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
                ml.update_item_playcount(content, id_, 1)
        self._playing_file = None
