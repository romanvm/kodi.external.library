# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from simpleplugin import Plugin

plugin = Plugin()
_ = plugin.initialize_gettext()


def root(params):
    """Root action"""
    if plugin.show_movies:
        yield {
            'label': '[{0}]'.format(_('Movies')),
            'url' : plugin.get_url(action='library_items', content='movies'),
            'thumb': 'DefaultMovies.png',
        }
    if plugin.show_tvshows:
        yield {
            'label': '[{0}]'.format(_('TV Shows')),
            'url' : plugin.get_url(action='library_items', content='tvshows'),
            'thumb': 'DefaultTVShows.png',
        }


plugin.actions['root'] = root
