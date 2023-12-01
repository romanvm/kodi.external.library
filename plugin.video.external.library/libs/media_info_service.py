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

from typing import Dict, Any, List, Tuple, Type
from urllib.parse import urljoin, quote

from xbmc import InfoTagVideo, Actor
from xbmcgui import ListItem

from libs.kodi_service import get_remote_kodi_url

__all__ = ['set_info', 'set_art']

REMOTE_KODI_URL = get_remote_kodi_url(with_credentials=True)
IMAGE_URL = urljoin(REMOTE_KODI_URL, 'image')


class SimpleMediaPropertySetter:
    """
    Sets a media property from a dictionary returned by JSON-RPC API to
    xbmc.InfoTagVideo class instance
    """

    def __init__(self, media_property: str, media_info: Dict[str, Any], info_tag_method: str):
        self._property_value = media_info.get(media_property)
        self._info_tag_method = info_tag_method

    def should_set(self) -> bool:
        return bool(self._property_value)

    def get_method_args(self) -> Tuple[Any, ...]:
        return (self._property_value,)

    def set_info_tag_property(self, info_tag: InfoTagVideo) -> None:
        args = self.get_method_args()
        method = getattr(info_tag, self._info_tag_method)
        method(*args)


class RatingsSetter(SimpleMediaPropertySetter):

    def get_method_args(self) -> Tuple[Any, ...]:
        ratings = {}
        defaultrating = ''
        for rating_type, rating_info in self._property_value.items():
            ratings[rating_type] = (rating_info.get('rating', 0.0), rating_info.get('votes', 0))
            if rating_info.get('default'):
                defaultrating = rating_type
        return ratings, defaultrating


class PlaycountSetter(SimpleMediaPropertySetter):

    def should_set(self) -> bool:
        return self._property_value is not None


class CastSetter(SimpleMediaPropertySetter):

    def get_method_args(self) -> Tuple[Any, ...]:
        actors = []
        for actor_info in self._property_value:
            actor_thumbnail = actor_info.get('thumbnail', '')
            if actor_thumbnail:
                actor_thumbnail = f'{IMAGE_URL}/{quote(actor_thumbnail)}'
            actors.append(Actor(
                name=actor_info.get('name', ''),
                role=actor_info.get('role', ''),
                order=actor_info.get('order') or -1,
                thumbnail=actor_thumbnail
            ))
        return (actors,)


class ResumePointSetter(SimpleMediaPropertySetter):

    def get_method_args(self) -> Tuple[Any, ...]:
        time = self._property_value.get('position', 0.0)
        totaltime = self._property_value.get('total', 0.0)
        return time, totaltime


# The list of 3 element tuples: (
#   media property name as returned by JSON-RPC call,
#   xbmc.InfoTagVideo method name,
#   media property handler class,
# )
"""
[
    'title',
    'genre',
    'year',
    'director',
    'trailer',
    'tagline',
    'plot',
    'plotoutline',
    'originaltitle',
    'playcount',
    'writer',
    'studio',
    'mpaa',
    'cast',
    'country',
    'set',
    'streamdetails',
    'top250',
    'votes',
    'file',
    'sorttitle',
    'resume',
    'setid',
    'dateadded',
    'tag',
    'art',
    'userrating',
    'ratings',
    'premiered',
]
"""
MEDIA_PROPERTIES: List[Tuple[str, str, Type[SimpleMediaPropertySetter]]] = [
    ('title', 'setTitle', SimpleMediaPropertySetter),
    ('genre', 'setGenres', SimpleMediaPropertySetter),
    ('year', 'setYear', SimpleMediaPropertySetter),
    ('director', 'setDirectors', SimpleMediaPropertySetter),
    ('trailer', 'setTrailer', SimpleMediaPropertySetter),
    ('tagline', 'setTagLine', SimpleMediaPropertySetter),
    ('plot', 'setPlot', SimpleMediaPropertySetter),
    ('plotoutline', 'setPlotOutline', SimpleMediaPropertySetter),
    ('playcount', 'setPlaycount', PlaycountSetter),
    ('writer', 'setWriters', SimpleMediaPropertySetter),
    ('studio', 'setStudios', SimpleMediaPropertySetter),
    ('mpaa', 'setMpaa', SimpleMediaPropertySetter),
    ('cast', 'setCast', CastSetter),
    ('country', 'setCountries', SimpleMediaPropertySetter),
    ('set', 'setSet', SimpleMediaPropertySetter),

    ('resume', 'setResumePoint', ResumePointSetter),

    ('ratings', 'setRatings', RatingsSetter),
    ('premiered', 'setPremiered', SimpleMediaPropertySetter),
    ('season', 'setSeason', SimpleMediaPropertySetter),
    ('episode', 'setEpisode', SimpleMediaPropertySetter),
]


def set_info(info_tag: InfoTagVideo, media_info: Dict[str, Any], mediatype: str) -> None:
    info_tag.setMediaType(mediatype)
    for media_property, info_tag_method, setter_class in MEDIA_PROPERTIES:
        setter = setter_class(media_property, media_info, info_tag_method)
        if setter.should_set():
            setter.set_info_tag_property(info_tag)


def set_art(list_item: ListItem, raw_art: Dict[str, str]) -> None:
    art = {art_type: f'{IMAGE_URL}/{quote(raw_url)}' for art_type, raw_url in raw_art.items()}
    list_item.setArt(art)
