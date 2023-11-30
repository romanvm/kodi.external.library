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
from typing import Dict, Any
from urllib.parse import quote, urljoin, parse_qsl

import xbmcplugin
from xbmc import InfoTagVideo, Actor
from xbmcgui import Dialog, ListItem

from libs.content_type_handlers import MoviesHandler, RecentMoviesHandler
from libs.exceptions import NoDataError, RemoteKodiError
from libs.kodi_service import (ADDON, ADDON_ID, GettextEmulator,
                               logger, get_remote_kodi_url, get_plugin_url)
from libs.mem_storage import MemStorage

_ = GettextEmulator.gettext

PLUGIN_URL = f'plugin://{ADDON_ID}/'
HANDLE = int(sys.argv[1])

DIALOG = Dialog()

REMOTE_KODI_URL = get_remote_kodi_url(with_credentials=True)
IMAGE_URL = urljoin(REMOTE_KODI_URL, 'image')
VIDEO_URL = urljoin(REMOTE_KODI_URL, 'vfs')


CONTENT_TYPE_HANDLERS = {
    'movies': MoviesHandler,
    'recent_movies': RecentMoviesHandler,
}


def root():
    """Root action"""
    xbmcplugin.setPluginCategory(HANDLE,
                                 _('Kodi Medialibrary on {kodi_host}').format(
                                     kodi_host=ADDON.getSetting('kodi_host')))
    if ADDON.getSettingBool('show_movies'):
        list_item = ListItem(f'[{_("Movies")}]')
        list_item.setArt({'icon': 'DefaultMovies.png', 'thumb': 'DefaultMovies.png'})
        url = get_plugin_url(content_type='movies')
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=True)
        if ADDON.getSettingBool('show_recent_movies'):
            list_item = ListItem(f'[{_("Recently added movies")}]')
            list_item.setArt({'icon': 'DefaultRecentlyAddedMovies.png',
                              'thumb': 'DefaultRecentlyAddedMovies.png'})
            url = get_plugin_url(content_type='recent_movies')
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=True)


def _set_art(list_item: ListItem, raw_art: Dict[str, str]) -> None:
    art = {art_type: f'{IMAGE_URL}/{quote(raw_url)}' for art_type, raw_url in raw_art.items()}
    list_item.setArt(art)


def _set_info(info_tag: InfoTagVideo, media_info: Dict[str, Any], mediatype: str) -> None:
    info_tag.setMediaType(mediatype)
    if year := media_info.get('year'):
        info_tag.setYear(year)
    if episode := media_info.get('episode'):
        info_tag.setEpisode(episode)
    if season := media_info.get('season'):
        info_tag.setSeason(season)
    if ratings := media_info.get('ratings'):
        for rating_type, rating_info in ratings.items():
            info_tag.setRating(rating=rating_info.get('rating', 0),
                               votes=rating_info.get('votes', 0),
                               type=rating_type,
                               isdefault=bool(rating_info.get('default')))
    if (playcount := media_info.get('playcount')) is not None:
        info_tag.setPlaycount(playcount)
    if mpaa := media_info.get('mpaa'):
        info_tag.setMpaa(mpaa)
    if plot := media_info.get('plot'):
        info_tag.setPlot(plot)
    if title := media_info.get('title'):
        info_tag.setTitle(title)
    if genres := media_info.get('genre'):
        info_tag.setGenres(genres)
    if countries := media_info.get('country'):
        info_tag.setCountries(countries)
    if directors := media_info.get('director'):
        info_tag.setDirectors(directors)
    if studios := media_info.get('studios'):
        info_tag.setStudios(studios)
    if writers := media_info.get('writer'):
        info_tag.setWriters(writers)
    if cast := media_info.get('cast'):
        actors = []
        for actor_info in cast:
            actor_thumbnail = actor_info.get('thumbnail', '')
            if actor_thumbnail:
                actor_thumbnail = f'{IMAGE_URL}/{quote(actor_thumbnail)}'
            actors.append(Actor(
                name=actor_info.get('name', ''),
                role=actor_info.get('role', ''),
                order=actor_info.get('order', 0),
                thumbnail=actor_thumbnail
            ))
        if actors:
            info_tag.setCast(actors)
    if premiered := media_info.get('premiered'):
        info_tag.setPremiered(premiered)
    if resume := media_info.get('resume'):
        info_tag.setResumePoint(time=resume.get('position', 0.0),
                                totaltime=resume.get('total', 0.0))


def show_media_items(content_type, tvshowid=None, season=None, parent_category=None):
    content_type_handler_class = CONTENT_TYPE_HANDLERS.get(content_type)
    if content_type_handler_class is None:
        raise RuntimeError(f'Unknown content type: {content_type}')
    content_type_handler = content_type_handler_class(tvshowid, season, parent_category)
    xbmcplugin.setPluginCategory(HANDLE, content_type_handler.get_plugin_category())
    xbmcplugin.setContent(HANDLE, content_type_handler.content)
    try:
        media_items = content_type_handler.get_media_items()
    except NoDataError:
        logger.exception('Unable to retrieve %s from the remote Kodi library',
                         content_type)
        DIALOG.notification(ADDON_ID, _('Unable to retrieve data from the remote Kodi library!'),
                            icon='error')
        return
    except RemoteKodiError as exc:
        logger.exception('Unable to connect to %s', str(exc))
        DIALOG.notification(ADDON_ID, _('Unable to connect to the remote Kodi host!'), icon='error')
        return
    logger.debug('Creating a list of %s items...', content_type)
    directory_items = []
    mem_storage_items = []
    for media_info in media_items:
        list_item = ListItem(media_info.get('title') or media_info.get('label', ''))
        if art := media_info.get('art'):
            _set_art(list_item, art)
        info_tag = list_item.getVideoInfoTag()
        _set_info(info_tag, media_info, content_type_handler.mediatype)
        list_item.addContextMenuItems(content_type_handler.get_item_context_menu(media_info))
        url = content_type_handler.get_item_url(media_info)
        directory_items.append((url, list_item, content_type_handler.item_is_folder))
        if content_type_handler.should_save_to_mem_storage:
            item_id_param = f'{content_type_handler.mediatype}id'
            mem_storage_items.append({
                'item_id_param': item_id_param,
                item_id_param: media_info[item_id_param],
                'file': media_info['file'],
            })
    xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))
    mem_storage = MemStorage()
    mem_storage['__external_library_list__'] = mem_storage_items
    logger.debug('Finished creating a list of %s items.', content_type)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    logger.debug('Called addon with params: %s', str(sys.argv))
    if 'content_type' not in params:
        root()
    else:
        if (tvshowid := params.get('tvshowid')) is not None:
            tvshowid = int(tvshowid)
        if (season := params.get('season')) is not None:
            season = int(season)
        parent_category = params.get('parent_category')
        show_media_items(params['content_type'], tvshowid, season, parent_category)
    xbmcplugin.endOfDirectory(HANDLE)
