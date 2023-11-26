# coding: utf-8
# Created on: 20.07.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from typing import Dict, Any
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


def get_url(**kwargs):
    return f'{PLUGIN_URL}?{urlencode(kwargs)}'


def root():
    """Root action"""
    if ADDON.getSettingBool('show_movies'):
        list_item = ListItem(f'[{_("Movies")}]')
        list_item.setArt({'icon': 'DefaultMovies.png', 'thumb': 'DefaultMovies.png'})
        url = get_url(content='movies')
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
    year = media_info.get('year')
    if year:
        info_tag.setYear(year)
    episode = media_info.get('episode')
    if episode:
        info_tag.setEpisode(episode)
    season = media_info.get('season')
    if season:
        info_tag.setSeason(season)
    ratings = media_info.get('ratings')
    if ratings:
        for rating_type, rating_info in ratings.items():
            info_tag.setRating(rating=rating_info.get('rating', 0),
                               votes=rating_info.get('votes', 0),
                               type=rating_type,
                               isdefault=bool(rating_info.get('default')))
    playcount = media_info.get('playcount')
    if playcount is not None:
        info_tag.setPlaycount(playcount)
    mpaa = media_info.get('mpaa')
    if mpaa:
        info_tag.setMpaa(mpaa)
    plot = media_info.get('plot')
    if plot:
        info_tag.setPlot(plot)
    title = media_info.get('title')
    if title:
        info_tag.setTitle(title)
    genres = media_info.get('genre')
    if genres:
        info_tag.setGenres(genres)
    countries = media_info.get('country')
    if countries:
        info_tag.setCountries(countries)
    directors = media_info.get('director')
    if directors:
        info_tag.setDirectors(directors)
    studios = media_info.get('studios')
    if studios:
        info_tag.setStudios(studios)
    writers = media_info.get('writer')
    if writers:
        info_tag.setWriters(writers)
    cast = media_info.get('cast')
    if cast:
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
    premiered = media_info.get('premiered')
    if premiered:
        info_tag.setPremiered(premiered)
    resume = media_info.get('resume')
    if resume:
        info_tag.setResumePoint(time=resume.get('position', 0.0), totaltime=resume.get('total', 0.0))


def show_movies():
    xbmcplugin.setPluginCategory(HANDLE, _('Movies'))
    xbmcplugin.setContent(HANDLE, 'movies')
    movies = medialibrary.get_movies()
    for mov in movies:
        list_item = ListItem(mov['label'])
        art = mov.get('art')
        if art:
            _set_art(list_item, art)
        info_tag = list_item.getVideoInfoTag()
        _set_info(info_tag, mov, 'movie')
        url = f'{VIDEO_URL}/{quote(mov["file"])}'
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=False)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    logger.debug('Called addon with params: %s', str(sys.argv))
    if 'content' not in params:
        root()
    xbmcplugin.endOfDirectory(HANDLE)
