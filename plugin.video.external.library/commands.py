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

import sys

import xbmc
import xbmcgui

from libs.exception_logger import catch_exception
from libs.json_rpc_api import SetMovieDetails, SetEpisodeDetails
from libs.kodi_service import GettextEmulator, logger

_ = GettextEmulator.gettext


API_MAP = {
    'movieid': SetMovieDetails,
    'episodeid': SetEpisodeDetails,
}


def update_playcount(item_id_param, item_id, playcount):
    api_class = API_MAP[item_id_param]
    api = api_class()
    api.set_details(**{item_id_param: item_id, 'playcount': playcount})
    xbmc.executebuiltin('Container.Refresh')


def main():
    if len(sys.argv) == 1:
        xbmcgui.Dialog().ok(_('External Kodi Medialibrary Client'),
                            _(r'Please run this addon from \"Video addons\" section.'))
        sys.exit(0)
    if sys.argv[1] == 'update_playcount':
        update_playcount(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))


if __name__ == '__main__':
    with catch_exception(logger.error):
        main()
