# coding: utf-8
# Created on: 25.11.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import base64
import pickle

import xbmcgui


class MemStorage:
    """
    Stores a picklable Python object as a Kodi window property

    This class can be used as an inter-process in-memory storage
    """
    def __init__(self, window_id=10000):
        self._window = xbmcgui.Window(window_id)

    def __getitem__(self, key):
        try:
            b64_value = pickle.loads(self._window.getProperty(key))
            return pickle.loads(base64.b64decode(b64_value))
        except (EOFError, KeyError, ValueError, pickle.PickleError) as exc:
            raise KeyError(f'Item "{key}" not found or invalid item!') from exc

    def __setitem__(self, key, value):
        pickled_value = pickle.dumps(value)
        self._window.setProperty(key, base64.b64encode(pickled_value).decode('ascii'))
