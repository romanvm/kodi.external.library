# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

from __future__ import division
from traceback import format_exc
from urllib import quote
import xbmc
from simpleplugin import Plugin
import libs.medialibrary as ml
from mem_storage import MemStorage

plugin = Plugin()


class PlayMonitor(xbmc.Player):
    """
    Monitors playback status and updates watches status
    for an episode or a movie from an external library
    """
    def __init__(self):
        super(PlayMonitor, self).__init__()
        self._storage = MemStorage()
        self.is_monitoring = False
        self._current_time = -1
        self._total_time = -1
        self._playing_file = None
        self._listing = None

    def onPlayBackStarted(self):
        if ml.kodi_url in self.getPlayingFile():
            self._playing_file = self.getPlayingFile()
            self.is_monitoring = True
            self._listing = self._storage['__list__']
            plugin.log_debug('Started monitoring {0}'.format(self._playing_file))
            try:
                self._total_time = self.getTotalTime()
            except:
                self._total_time = -1

    def onPlayBackStopped(self):
        self._update_watched()

    def onPlayBackEnded(self):
        self._update_watched()

    def update_time(self):
        try:
            self._current_time = self.getTime()
        except:
            self._current_time = -1
        if self._total_time == -1:
            try:
                self._total_time = self.getTotalTime()
            except:
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
                (self._current_time / self._total_time) >= plugin.watched_threshold):
            try:
                content, id_ = self._get_item_info()
            except RuntimeError:
                plugin.log_error(format_exc())
            else:
                plugin.log_debug('Updating watched status for {0} {1}'.format(content[:-1], self._playing_file))
                ml.update_item_playcount(content, id_, 1)
        self._playing_file = None
