# coding: utf-8
# Created on: 22.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xbmc
import libs.medialibrary as ml


class MyPlayer(xbmc.Player):
    current_time = -1
    total_time = -1
    info_tag = None

    def onPlayBackStarted(self):
        try:
            self.total_time = self.getTotalTime()
        except:
            self.total_time = -1
        if self.isPlayingVideo():
            self.info_tag = self.getVideoInfoTag()

    def onPlayBackStopped(self):
        self._update_watched()

    def onPlayBackEnded(self):
        self._update_watched()

    def update_time(self):
        try:
            self.current_time = self.getTime()
        except:
            self.current_time = -1
        if self.total_time <= 0:
            try:
                self.total_time = self.getTotalTime()
            except:
                self.total_time = -1

    def _update_watched(self):
        xbmc.log('%%%%%%%%%%%%%%%%%%%%%%%% {}'.format(self.info_tag.getIMDBNumber()))

#
# player = MyPlayer()
#
# while not xbmc.abortRequested:
#     xbmc.sleep(200)
#     if player.isPlaying():
#         player.update_time()
