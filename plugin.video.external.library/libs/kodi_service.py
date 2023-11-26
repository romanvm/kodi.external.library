# coding: utf-8
# (c) Roman Miroshnychenko <roman1972@gmail.com> 2020
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

"""Classes and functions to interact with Kodi API"""
import hashlib
import inspect
import os
import pickle
import re
from pathlib import Path

import xbmc
from xbmcaddon import Addon
from xbmcvfs import translatePath

ADDON = Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')

ADDON_DIR = Path(translatePath(ADDON.getAddonInfo('path')))
ADDON_ICON = Path(translatePath(ADDON.getAddonInfo('icon')))
ADDON_PROFILE_DIR = Path(translatePath(ADDON.getAddonInfo('profile')))


class logger:  # pylint: disable=invalid-name
    # pylint: disable=missing-docstring
    FORMAT = '[{id} v.{version}] - {filename}:{lineno} - {message}'

    @classmethod
    def _write_message(cls, message, *args, level=xbmc.LOGDEBUG):
        if args:
            message = message % args
        curr_frame = inspect.currentframe()
        xbmc.log(
            cls.FORMAT.format(
                id=ADDON_ID,
                version=ADDON_VERSION,
                filename=os.path.basename(curr_frame.f_back.f_back.f_code.co_filename),
                lineno=curr_frame.f_back.f_back.f_lineno,
                message=message
            ),
            level
        )

    @classmethod
    def info(cls, message, *args):
        cls._write_message(message, *args, level=xbmc.LOGINFO)

    @classmethod
    def warning(cls, message, *args):
        cls._write_message(message, *args, level=xbmc.LOGWARNING)

    @classmethod
    def error(cls, message, *args):
        cls._write_message(message, *args, level=xbmc.LOGERROR)

    @classmethod
    def debug(cls, message, *args):
        cls._write_message(message, *args, level=xbmc.LOGDEBUG)


class GettextEmulator:
    """Emulate GNU Gettext by mapping resource.language.en_gb UI strings to their numeric string IDs"""
    _instance = None

    class LocalizationError(Exception):  # pylint: disable=missing-docstring
        pass

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(*args, **kwargs)
        return cls._instance

    def __init__(self):
        self._en_gb_string_po_path = ADDON_DIR / 'resources' / 'language' / 'resource.language.en_gb' / 'strings.po'
        if not self._en_gb_string_po_path.exists():
            raise self.LocalizationError('Missing resource.language.en_gb strings.po localization file')
        if not ADDON_PROFILE_DIR.exists():
            ADDON_PROFILE_DIR.mkdir()
        self._string_mapping_path = ADDON_PROFILE_DIR / 'strings-map.pickle'
        self.strings_mapping = self._load_strings_mapping()

    def _load_strings_po(self):  # pylint: disable=missing-docstring
        with self._en_gb_string_po_path.open('r', encoding='utf-8') as fo:
            return fo.read()

    def _load_strings_mapping(self):
        """
        Load mapping of resource.language.en_gb UI strings to their IDs

        If a mapping file is missing or resource.language.en_gb strins.po file has been updated,
        a new mapping file is created.

        :return: UI strings mapping
        """
        strings_po = self._load_strings_po()
        strings_po_md5 = hashlib.md5(strings_po.encode('utf-8')).hexdigest()
        try:
            with self._string_mapping_path.open('rb') as fo:
                mapping = pickle.load(fo)
            if mapping['md5'] != strings_po_md5:
                raise IOError('resource.language.en_gb strings.po has been updated')
        except (IOError, pickle.PickleError):
            strings_mapping = self._parse_strings_po(strings_po)
            mapping = {
                'strings': strings_mapping,
                'md5': strings_po_md5,
            }
            with self._string_mapping_path.open('wb') as fo:
                pickle.dump(mapping, fo)
        return mapping['strings']

    @staticmethod
    def _parse_strings_po(strings_po):
        """
        Parse resource.language.en_gb strings.po file contents into a mapping of UI strings
        to their numeric IDs.

        :param strings_po: the content of strings.po file as a text string
        :return: UI strings mapping
        """
        id_string_pairs = re.findall(r'^msgctxt "#(\d+?)"\r?\nmsgid "(.*)"\r?$', strings_po, re.M)
        return {string: int(string_id) for string_id, string in id_string_pairs if string}

    @classmethod
    def gettext(cls, en_string):
        """
        Return a localized UI string by a resource.language.en_gb source string

        :param en_string: resource.language.en_gb UI string
        :return: localized UI string
        """
        emulator = cls()
        try:
            string_id = emulator.strings_mapping[en_string]
        except KeyError:
            raise cls.LocalizationError(
                f'Unable to find resource.language.en_gb string "{en_string}" in strings.po')
        return ADDON.getLocalizedString(string_id)


def get_kodi_url(with_credentials=False):
    host = ADDON.getSetting('kodi_host')
    port = ADDON.getSetting('kodi_port')
    login = ADDON.getSetting('kodi_login')
    password = ADDON.getSetting('kodi_password')
    if not with_credentials or not login:
        return f'http://{host}:{port}'
    return f'http://{login}:{password}@{host}:{port}'
