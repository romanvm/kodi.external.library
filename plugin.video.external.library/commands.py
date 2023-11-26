# coding: utf-8
# Created on: 22.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys

import xbmc

from libs import medialibrary as ml

if __name__ == '__main__':
    if sys.argv[1] == 'update_playcount':
        ml.update_item_playcount(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
        xbmc.executebuiltin('Container.Refresh')
