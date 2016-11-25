# coding: utf-8
# Created on: 25.11.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xbmc
from libs.monitor import PlayMonitor

monitor = PlayMonitor()

while not xbmc.abortRequested:
    xbmc.sleep(333)
    if monitor.isPlaying() and monitor.is_monitoring:
        monitor.update_time()
