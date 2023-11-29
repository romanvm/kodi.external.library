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

from libs import medialibrary_api as ml

if __name__ == '__main__':
    if sys.argv[1] == 'update_playcount':
        ml.update_item_playcount(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
        xbmc.executebuiltin('Container.Refresh')
