# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
from urllib import quote
from xbmcgui import Dialog
from simpleplugin import Plugin
import medialibrary as ml

plugin = Plugin()
_ = plugin.initialize_gettext()
dialog = Dialog()
image_url = ml.kodi_url + '/image/'
commands = os.path.join(plugin.path, 'libs', 'commands.py')


@plugin.action()
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


def _set_info(content, item, list_item):
    """
    Set list item info
    """
    video_info = {'title': item['label']}
    if content.endswith('movies') or content == 'tvshows':
        video_info['genre'] = u', '.join(item['genre'])
        video_info['year'] = item['year']
        video_info['plot'] = item['plot']
        video_info['cast'] = [actor['name'] for actor in item['cast']]
        video_info['studio'] = u', '.join(item['studio'])
        if content.endswith('movies'):
            video_info['director'] = u', '.join(item['director'])
    elif content == 'seasons':
        video_info['tvshowtitle'] = item['showtitle']
        video_info['season'] = item['season']
    elif content.endswith('episodes'):
        video_info['tvshowtitle'] = item['showtitle']
        video_info['plot'] = item['plot']
        video_info['cast'] = [actor['name'] for actor in item['cast']]
        video_info['director'] = u', '.join(item['director'])
        video_info['premiered'] = item['firstaired']
        video_info['season'] = item['season']
        video_info['episode'] = item['episode']
        if content == 'recent_episodes':
            list_item['label'] = video_info['title'] = u'{0} - {1}'.format(item['showtitle'], item['label'])
    list_item['info']['video'] = video_info


def _set_art(content, item, list_item):
    """
    Set list item artwork
    """
    if content.endswith('movies'):
        list_item['thumb'] = list_item['art']['poster'] = image_url + quote(item['art'].get('poster', ''))
        list_item['fanart'] = image_url + quote(item['art'].get('fanart', ''))
    elif content == 'tvshows':
        list_item['thumb'] = list_item['art']['poster'] = image_url + quote(
            item['art'].get('tvshow.poster') or
            item['art'].get('poster', '')
        )
        list_item['art']['banner'] = image_url + quote(
            item['art'].get('tvshow.banner') or
            item['art'].get('banner', '')
        )
        list_item['fanart'] = image_url + quote(
            item['art'].get('tvshow.fanart') or
            item['art'].get('fanart')
        )
    elif content == 'seasons':
        list_item['thumb'] = list_item['art']['poster'] = image_url + quote(
            item['art'].get('season.poster') or
            item['art'].get('tvshow.poster') or
            item['art'].get('poster', '')
        )
        list_item['art']['banner'] = image_url + quote(
            item['art'].get('season.banner') or
            item['art'].get('tvshow.banner') or
            item['art'].get('banner', '')
        )
        list_item['fanart'] = image_url + quote(
            item['art'].get('season.fanart') or
            item['art'].get('tvshow.fanart') or
            item['art'].get('fanart', '')
        )
    elif content.endswith('episodes'):
        list_item['thumb'] = image_url + quote(
            item['art'].get('thumb', '') or
            item['art'].get('season.poster') or
            item['art'].get('tvshow.poster') or
            item['art'].get('poster', '')
        )
        list_item['poster'] = image_url + quote(
            item['art'].get('season.poster') or
            item['art'].get('tvshow.poster') or
            item['art'].get('poster', '')
        )
        list_item['art']['banner'] = image_url + quote(
            item['art'].get('season.banner') or
            item['art'].get('tvshow.banner') or
            item['art'].get('banner', '')
        )
        list_item['fanart'] = image_url + quote(
            item['art'].get('season.fanart') or
            item['art'].get('tvshow.fanart') or
            item['art'].get('fanart', '')
        )


def _show_library_items(items, content):
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
            'thumb': 'DefaultRecentlyAddedEpisodes.png'
        }
    for item in items:
        list_item = {'label': item['label'], 'art': {}, 'info': {}}
        _set_info(content, item, list_item)
        _set_art(content, item, list_item)
        if content.endswith('movies') or content.endswith('episodes'):
            if item['playcount']:
                caption = '[COLOR=yellow]{0}[/COLOR]'.format(_('Mark as unwatched'))
                playcount = 0
            else:
                caption = '[COLOR=green]{0}[/COLOR]'.format(_('Mark as watched'))
                playcount = 1
            if content.endswith('movies'):
                item_id = item['movieid']
            else:
                item_id = item['episodeid']
            list_item['context_menu'] = [(
                caption, 'RunScript({commands},update_playcount,{content},{id},{playcount})'.format(
                    commands=commands,
                    content=content,
                    id=item_id,
                    playcount=playcount
                )
            )]
            list_item['info']['video']['playcount'] = item['playcount']
            list_item['url'] = ml.kodi_url + '/vfs/' + quote(item['file'])
            # list_item['url'] = plugin.get_url(action='play', file=item['file'])
            list_item['is_playable'] = True
        elif content == 'tvshows':
            list_item['url'] = plugin.get_url(action='library_items', content='seasons', tvshowid=item['tvshowid'])
        elif content == 'seasons':
            list_item['url'] = plugin.get_url(action='library_items', content='episodes',
                                              tvshowid=item['tvshowid'], season=item['season'])
        plugin.log('List item: {0}'.format(list_item))
        yield list_item


@plugin.action()
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
        elif content == 'seasons':
            items = ml.get_seasons(int(params['tvshowid']))
            plugin_content = 'tvshows'
            if (plugin.flatten_tvshows == 1 and len(items) == 1) or plugin.flatten_tvshows == 2:
                items = ml.get_episodes(int(params['tvshowid']), items[0]['season'])
                content = plugin_content = 'episodes'
        elif content.endswith('episodes'):
            items = ml.get_episodes(int(params.get('tvshowid', -1)),
                                    int(params.get('season', -1)),
                                    content.startswith('recent'))
            plugin_content = 'episodes'
    except ml.ConnectionError:
        dialog.notification(plugin.id, _('Unable to connect to the remote Kodi host!'), icon='error')
    except ml.NoDataError:
        dialog.notification(plugin.id, _('Remote Kodi library contains no relevant data!'), icon='error')
    else:
        listing = _show_library_items(items, content)
    return plugin.create_listing(listing, content=plugin_content)
