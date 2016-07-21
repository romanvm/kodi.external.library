# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from urllib import quote_plus
from xbmcgui import Dialog
from simpleplugin import Plugin
import medialibrary as ml

plugin = Plugin()
_ = plugin.initialize_gettext()
dialog = Dialog()
image_url = ml.kodi_url + '/image/'


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


def _show_library_items(items, content, tvshow_details=None):
    """
    Get the list of movies or TV shows
    """
    if content == 'movies' and plugin.show_recent_movies:
        yield {
            'label': '[{0}]'.format(_('Recently added movies')),
            'url': plugin.get_url(action='library_items', content='recent_movies'),
            'thumb': 'DefaultRecentlyAddedMovies.png'
        }
    elif content == 'tvshows' and plugin.show_recent_episodes:
        yield {
            'label': '[{0}]'.format(_('Recently added episodes')),
            'url'  : plugin.get_url(action='library_items', content='recent_episodes'),
            'thumb': 'DefaultRecentlyAddedMovies.png'
        }
    for item in items:
        list_item = {
            'label': item['label'],
            'thumb': image_url + quote_plus(item['art'].get('poster', '')),
            'fanart': image_url + quote_plus(item['art'].get('fanart', '')),
            'art': {'poster': image_url + quote_plus(item['art'].get('poster', ''))},
            'info': {
                'video': {
                    'imdbnumber': item['imdbnumber'],
                    'title': item['title'],
                    'cast': [actor['name'] for actor in item['cast']],
                    'year': item['year'],
                    'genre': u', '.join(item['genre']),
                    'plot': item['plot']
                    }
                }
            }
        if content.endswith('movies'):
            list_item['info']['video']['director'] = item['director']
            list_item['info']['video']['playcount'] = item['playcount']
            list_item['url'] = ml.kodi_url + '/vfs/' + quote_plus(item['file'])
            list_item['is_playable'] = True
        elif content == 'tvshows':
            list_item['url'] = plugin.get_url(action='library_items', content='seasons', tvshowid=item['tvshowid'])
        yield list_item


def library_items(params):
    """
    Display the list of movies or TV shows
    """
    listing = []
    plugin_content = None
    content = params['content']
    try:
        if content.endswith('movies'):
            items = ml.get_movies(recent=content.startswith('recent'))
            plugin_content = 'movies'
        elif content == 'tvshows':
            items = ml.get_tvshows()
            plugin_content = 'tvshows'
    except ml.ConnectionError:
        dialog.notification(plugin.id, _('Unable to connect to the remote Kodi host!'), icon='error')
    except ml.NoDataError:
        dialog.notification(plugin.id, _('Remote Kodi library contains no relevant data!'), icon='error')
    else:
        listing = _show_library_items(items, content)
    return plugin.create_listing(listing, content=plugin_content)


plugin.actions['root'] = root
plugin.actions['library_items'] = library_items
