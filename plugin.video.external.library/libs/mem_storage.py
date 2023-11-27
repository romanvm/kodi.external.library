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

import base64
import pickle

import xbmcgui


class MemStorage:
    """
    Stores a picklable Python object in a shared memory within Kodi

    It can be used to exchange data between different Python scripts running inside Kodi.
    """
    def __init__(self, window_id=10000):
        self._window = xbmcgui.Window(window_id)

    def __getitem__(self, key):
        try:
            b64_value = self._window.getProperty(key)
            return pickle.loads(base64.b64decode(b64_value))
        except (EOFError, KeyError, ValueError, pickle.PickleError) as exc:
            raise KeyError(f'Item "{key}" not found or invalid item!') from exc

    def __setitem__(self, key, value):
        pickled_value = pickle.dumps(value)
        self._window.setProperty(key, base64.b64encode(pickled_value).decode('ascii'))

    def __delitem__(self, key):
        self._window.clearProperty(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
