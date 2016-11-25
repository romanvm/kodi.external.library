# coding: utf-8
# Created on: 25.11.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import cPickle as pickle
from base64 import standard_b64encode
import xbmcgui


class MemStorage(object):
    """
    Stores a picklable Python object as a Kodi window property

    This class can be used as an inter-process in-memory storage
    """
    def __init__(self, window_id=10000):
        self._window = xbmcgui.Window(window_id)

    def __getitem__(self, item):
        self.check_key_type(item)
        try:
            return pickle.loads(self._window.getProperty(standard_b64encode(item)))
        except (EOFError, KeyError, pickle.PickleError):
            raise KeyError('Item "{0}" not found or invalid item!'.format(item))

    def __setitem__(self, key, value):
        self.check_key_type(key)
        self._window.setProperty(standard_b64encode(key), pickle.dumps(value))

    def __contains__(self, item):
        self.check_key_type(item)
        try:
            self[item]
        except KeyError:
            return False
        return True

    def get(self, item, default=None):
        self.check_key_type(item)
        try:
            return self[item]
        except KeyError:
            return default

    @staticmethod
    def check_key_type(key):
        if not isinstance(key, str):
            raise TypeError('Storage key must be of str type!')
