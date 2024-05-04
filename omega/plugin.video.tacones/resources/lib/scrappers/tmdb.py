# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright 2023 Someone Like You
#
# This file is part of the modification by SomeoneLikeYou of LiveStreamsPro.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Inspired by Alfa Addon
# URL: https://github.com/alfa-addon/addon/tree/master/plugin.video.alfa/core
# ------------------------------------------------------------------------------

import re
import copy
from . import LSPScrapper
from six.moves import urllib_parse


class TMDBScrapper(LSPScrapper):
    """
    Get's information from https://www.themoviedb.org/
    """

    def __init__(self):
        super().__init__("TMDB")
        self.provider = "TMDB"
        self.TMDB_IMAGE_PATH = "https://image.tmdb.org/t/p/original"
        self.API_KEY = "48e8b0532d3b7728108a8245fd4551b2"
        self.language = "es"
        self.PARAMS = {'api_key': self.API_KEY, 'language': self.language,
                       'append_to_response': 'images,videos,external_ids,credits',
                       'include_image_language': '%s,null' % (self.language)}
        self.results = {}

    def getMoreInformation(self, item):
        tmdbId = item.get('tmdb', None)
        return self.get_by_id(
            item) if tmdbId is not None else self.search_tmdb(item)

    def search_tmdb(self, item, page=1, retry=True):
        mediatype = item.get('mediatype')
        contentTitle = item.get('contentTitle') if item.get(
            'contentTitle', None) is not None else item.get('title')
        cleanTextTitle = urllib_parse.quote(re.sub(
            self.cleanTextRegex, '', re.sub(self.cleanTextRegex, '', contentTitle)))
        url = 'https://api.themoviedb.org/3/search/%s' % (mediatype)
        searchParams = {
            'api_key': self.API_KEY, 'query': cleanTextTitle,
            'include_adult': 'false', 'page': str(page),
            'language': self.language
        }
        if item.get('year'):
            if mediatype == 'movie':
                searchParams['primary_release_year'] = item.get('year')
            else:
                searchParams['first_air_date_year'] = item.get('year')
        url += ('&', '?')[urllib_parse.urlparse(url).query == ''] + \
            '&'.join(["{}={}".format(k, v)
                     for k, v in searchParams.items()])
        response = self._GET(url)
        if len(response['results']) == 0:
            # Volvemos a hacer la llamada pero esta vez sin el año para obtener un resultado más amplio
            item['year'] = None
            if retry:
                return self.search_tmdb(item, retry=False)
            else:
                raise Exception(
                    "TMDB cannot be found, title: %s, url: %s" % (contentTitle, url))
        if 'id' in response['results'][0]:
            item['tmdb'] = response['results'][0]['id']
            return self.get_by_id(item)
        return response['results'][0]

    def get_by_id(self, item):
        contentType = 'movie' if item.get('mediatype') == 'movie' else 'tv'
        url = "https://api.themoviedb.org/3/%s/%s" % (
            contentType, item.get('tmdb'))
        if item.get('mediatype') == 'season':
            seasonNumber = item.get('season', None)
            if seasonNumber is None:
                raise Exception('Season not specified')
            url += '/season/%s' % (str(seasonNumber))
        elif item.get('mediatype') == 'episode':
            seasonNumber = item.get('season', None)
            episodeNumber = item.get('episode', None)
            if seasonNumber is None or episodeNumber is None:
                raise Exception('Season or episode not specified')
            url += '/season/%s/episode/%s' % (str(seasonNumber),
                                              str(episodeNumber))
        url += ('&', '?')[urllib_parse.urlparse(url).query == ''] + \
            '&'.join(["{}={}".format(k, v)
                     for k, v in self.PARAMS.items()])
        response = self._GET(url)
        return response

    def iterateItemMovie(self, providerItem):
        kodiItem = dict()
        newItem = self.parseImages(copy.deepcopy(providerItem))
        tmdbMoviePair = {
            'tmdb_id': 'id',
            'backdrop_path': 'backdrop_path',
            'thumbnail': 'poster_path',
            'poster_path': 'poster_path',
            'tagline': 'tagline',
            'title': 'title',
            'plot': 'overview',
            'release_date': 'release_date'
        }
        for k, v in tmdbMoviePair.items():
            if v in newItem:
                kodiItem[k] = newItem[v]

        kodiItem['genres'] = ", ".join(
            [genre['name'] for genre in newItem['genres']])
        kodiItem['duration'] = newItem['runtime'] * 60
        kodiItem['popularity'] = float(round(newItem['vote_average'], 2))
        kodiItem['imdb'] = newItem['external_ids']['imdb_id']
        kodiItem['year'] = newItem['release_date'][:4]
        kodiItem['trailer'] = self.get_videos('movie',
                                              providerItem.get('id'), newItem['videos']['results'])
        kodiItem['cast'] = newItem['credits']['cast']
        # kodiItem['crew'] = newItem['credits']['crew']
        return kodiItem

    def iterateItemShow(self, providerItem):
        kodiItem = dict()
        newItem = self.parseImages(copy.deepcopy(providerItem))

        kodiItem['tmdb_id'] = newItem['id']
        kodiItem['backdrop_path'] = newItem['backdrop_path']
        kodiItem['thumbnail'] = newItem['poster_path']
        kodiItem['poster_path'] = newItem['poster_path']
        kodiItem['tagline'] = newItem['tagline']
        kodiItem['title'] = newItem['name']
        kodiItem['plot'] = newItem['overview']
        kodiItem['genres'] = ", ".join(
            [genre['name'] for genre in newItem['genres']])
        if len(newItem['episode_run_time']) > 0:
            kodiItem['duration'] = newItem['episode_run_time'][0] * 60
        else:
            kodiItem['duration'] = 50 * 60
        kodiItem['popularity'] = float(round(newItem['vote_average'], 2))
        kodiItem['imdb'] = newItem['external_ids']['imdb_id']
        kodiItem['year'] = newItem['last_air_date'][:4]
        kodiItem['release_date'] = newItem['last_air_date']
        kodiItem['trailer'] = self.get_videos('tv',
                                              providerItem.get('id'), newItem['videos']['results'])
        kodiItem['cast'] = newItem['credits']['cast']
        # kodiItem['crew'] = newItem['credits']['crew']
        return kodiItem

    def iterateItemSeason(self, providerItem):
        kodiItem = dict()
        newItem = self.parseImages(copy.deepcopy(providerItem))
        tmdbSeasonPair = {
            'backdrop_path': 'backdrop_path',
            'thumbnail': 'poster_path',
            'poster_path': 'poster_path',
            'tagline': 'tagline',
            'title': 'name',
            'plot': 'overview',
            'release_date': 'air_date'
        }
        for k, v in tmdbSeasonPair.items():
            if v in newItem:
                kodiItem[k] = newItem[v]
        if 'air_date' in newItem:
            kodiItem['year'] = newItem['air_date'][:4]
        if 'runtime' in newItem:
            kodiItem['duration'] = newItem['runtime'] * 60
        else:
            kodiItem['duration'] = 50 * 60
        return kodiItem

    def iterateItemEpisode(self, providerItem):
        kodiItem = dict()
        newItem = self.parseImages(copy.deepcopy(providerItem))
        tmdbEpisodePair = {
            'tmdb_id': 'id',
            'backdrop_path': 'backdrop_path',
            'thumbnail': 'still_path',
            'poster_path': 'still_path',
            'tagline': 'tagline',
            'title': 'name',
            'plot': 'overview',
            'release_date': 'air_date'
        }
        for k, v in tmdbEpisodePair.items():
            if v in newItem:
                kodiItem[k] = newItem[v]
        if 'runtime' in newItem:
            kodiItem['duration'] = str(newItem['runtime'] * 60)
        else:
            kodiItem['duration'] = str(50 * 60)
        if 'popularity' in newItem:
            kodiItem['popularity'] = float(round(newItem['vote_average'], 2))
        if 'air_date' in newItem:
            kodiItem['year'] = newItem['air_date'][:4]
        if 'credits' in newItem:
            kodiItem['cast'] = newItem['credits']['cast']
        # kodiItem['crew'] = newItem['credits']['crew']
        return kodiItem

    def get_videos(self, mediatype, providerId, providerResults=None):
        kodiVideos = list()
        if providerResults is None or len(providerResults) == 0:
            videosUrl = "https://api.themoviedb.org/3/{}/{}/videos?api_key={}&language=en-US".format(
                mediatype, providerId, self.API_KEY)
            videosResponse = self._GET(videosUrl)
            if not 'results' in videosResponse:
                return []
            providerResults = videosResponse['results']
        for video in providerResults:
            if not video.get('official') or video.get('site').lower() != 'youtube':
                continue
            kodiVideos.append({'name': video.get(
                'name'), 'quality': video.get('size'),
                'url': "https://www.youtube.com/watch?v={}".format(video.get('key'))})
        return kodiVideos

    def parseImages(self, item):
        # The API provides a relative path for the images, so we need to change it
        for k, v in item.items():
            if isinstance(v, str):
                if (".jpg" in str(v) or ".png" in str(v)) and not str(v).startswith('http'):
                    item[k] = self.TMDB_IMAGE_PATH + str(v)
            elif isinstance(v, list):
                for dictionary in v:
                    if isinstance(dictionary, dict):
                        for dk, dv in dictionary.items():
                            if (".jpg" in str(dv) or ".png" in str(dv)) and not str(dv).startswith('http'):
                                dictionary[dk] = self.TMDB_IMAGE_PATH + str(dv)
            elif isinstance(v, dict):
                for dk, dv in v.items():
                    if isinstance(dv, str):
                        if (".jpg" in str(dv) or ".png" in str(dv)) and not str(dv).startswith('http'):
                            item[k][dk] = self.TMDB_IMAGE_PATH + str(dv)
                    elif isinstance(dv, list):
                        for dictionary in dv:
                            for ddk, ddv in dictionary.items():
                                if (".jpg" in str(ddv) or ".png" in str(ddv)) and not str(ddv).startswith('http'):
                                    dictionary[ddk] = self.TMDB_IMAGE_PATH + \
                                        str(ddv)
        return item
