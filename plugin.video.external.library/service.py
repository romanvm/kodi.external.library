# coding: utf-8
# Created on: 25.11.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from __future__ import division
from urllib import quote
import xbmc
from simpleplugin import Plugin
import libs.medialibrary as medialibrary
from libs.mem_storage import MemStorage

plugin = Plugin()


class MyPlayer(xbmc.Player):

    def __init__(self):
        super(MyPlayer, self).__init__()
        self._storage = MemStorage()
        self.is_monitoring = False
        self._current_time = -1
        self._total_time = -1
        self._playing_file = None

    def onPlayBackStarted(self):
        if medialibrary.kodi_url in self.getPlayingFile():
            self._playing_file = self.getPlayingFile()
            self.is_monitoring = True
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
        if self._total_time <= 0:
            try:
                self._total_time = self.getTotalTime()
            except:
                self._total_time = -1

    def _get_item_info(self):
        listing = self._storage['__list__']
        plugin.log_notice(listing)
        for item in listing:
            if quote(item['file']) in self._playing_file:
                if 'movieid' in item:
                    content = 'movies'
                    id_ = item['movieid']
                else:
                    content = 'episodes'
                    id_ = item['episodeid']
                return content, id_

    def _update_watched(self):
        self.is_monitoring = False
        if self._current_time != -1 and self._total_time != -1 and self._current_time / self._total_time >= 0.97:
            content, id_ = self._get_item_info()
            medialibrary.update_item_playcount(content, id_, 1)
        self._playing_file = None


player = MyPlayer()

while not xbmc.abortRequested:
    xbmc.sleep(200)
    if player.isPlaying() and player.is_monitoring:
        player.update_time()
