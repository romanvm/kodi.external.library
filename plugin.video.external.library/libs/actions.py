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
from typing import Dict, Any, NamedTuple, Type, Callable
from urllib.parse import quote, urljoin, parse_qsl, urlencode

import xbmcplugin
from xbmc import InfoTagVideo, Actor
from xbmcgui import Dialog, ListItem

from libs import medialibrary
from libs.kodi_service import ADDON, ADDON_ID, GettextEmulator, logger, get_kodi_url
from libs.mem_storage import MemStorage

_ = GettextEmulator.gettext

PLUGIN_URL = f'plugin://{ADDON_ID}/'
HANDLE = int(sys.argv[1])

DIALOG = Dialog()
STORAGE = MemStorage()

KODI_URL = get_kodi_url(with_credentials=True)
IMAGE_URL = urljoin(KODI_URL, 'image')
VIDEO_URL = urljoin(KODI_URL, 'vfs')


class ContentTypeInfo(NamedTuple):
    content: str
    mediatype: str
    plugin_category: str
    handler_class: Type[medialibrary.BaseMediaItemsRetriever]
    get_url_func: Callable[[Dict[str, Any]], str]


def _get_plugin_url(**kwargs):
    return f'{PLUGIN_URL}?{urlencode(kwargs)}'


def get_videofile_url(media_info):
    return f'{VIDEO_URL}/{quote(media_info["file"])}'


def get_seasons_url(media_info):
    return _get_plugin_url(content_type='seasons', tvshowid=str(media_info['tvshowid']))


def get_episodes_url(media_info):
    return _get_plugin_url(content_type='episodes', tvshowid=str(media_info['tvshowid']))


CONTENT_TYPE_MAP = {
    'movies': ContentTypeInfo('movies', 'movie',
                              _('Movies'), medialibrary.Movies, get_videofile_url),
    'recent_movies': ContentTypeInfo('movies', 'movie',
                                     _('Recent Movies'), medialibrary.RecentMovies, get_videofile_url),
}


def root():
    """Root action"""
    xbmcplugin.setPluginCategory(HANDLE,
                                 _('Kodi Medialibrary on {kodi_host}').format(
                                     kodi_host=ADDON.getSetting('kodi_host')))
    if ADDON.getSettingBool('show_movies'):
        list_item = ListItem(f'[{_("Movies")}]')
        list_item.setArt({'icon': 'DefaultMovies.png', 'thumb': 'DefaultMovies.png'})
        url = _get_plugin_url(content_type='movies')
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=True)
    # if ADDON.getSettingBool('show_tvshows'):
    #     list_item = ListItem(f'[{_("TV Shows")}]')
    #     list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': 'DefaultTVShows.png'})
    #     url = get_url(content='tvshows')
    #     xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=True)


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
        info_tag.setResumePoint(time=resume.get('position', 0.0), totaltime=resume.get('total', 0.0))


def show_media_items(content_type, tvshowid=None, season=None):
    content_type_info = CONTENT_TYPE_MAP.get(content_type)
    if content_type_info is None:
        logger.error('Unknown content type: %s', content_type)
        return
    xbmcplugin.setPluginCategory(HANDLE, content_type_info.plugin_category)
    xbmcplugin.setContent(HANDLE, content_type_info.content)
    handler_class = content_type_info.handler_class
    handler_class.content = content_type_info.content
    handler_class.tvshowid = tvshowid
    handler_class.season = season
    media_items = content_type_info.handler_class().get_media_items()
    logger.debug('Creating a list of %s items...', content_type)
    for media_info in media_items:
        list_item = ListItem(media_info.get('title') or media_info.get('label'))
        if art := media_info.get('art'):
            _set_art(list_item, art)
        info_tag = list_item.getVideoInfoTag()
        _set_info(info_tag, media_info, content_type_info.mediatype)
        url = content_type_info.get_url_func(media_info)
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=False)
    logger.debug('Finished creating a of %s items.', content_type)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    logger.debug('Called addon with params: %s', str(sys.argv))
    if 'content_type' not in params:
        root()
    else:
        tvshowid = params.get('tvshowid')
        if tvshowid is not None:
            tvshowid = int(tvshowid)
        season = params.get('season')
        if season is not None:
            season = int(season)
        show_media_items(params['content_type'], tvshowid, season)
    xbmcplugin.endOfDirectory(HANDLE)
