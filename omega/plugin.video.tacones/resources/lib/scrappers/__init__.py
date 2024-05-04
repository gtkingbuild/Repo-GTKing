# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright 2023 Someone Like You
#
# This file is part of the modification by SomeoneLikeYou of LiveStreamsPro.
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
# ------------------------------------------------------------------------------

import sqlite3
import os
import json
import requests
import requests
import threading
import base64

import xbmcaddon
import xbmc
import xbmcvfs
ADDON = xbmcaddon.Addon()
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
DB_FILE = os.path.join(PROFILE, "provider_data.db")


class LSPScrapper(object):
    """Parent object of the kodi metadata scrappers"""

    def __init__(self, provider) -> None:
        """Initialize the parent object"""
        self.provider = provider
        self.cleanTextRegex = r'\[\/?(B|I|COLOR)[^\]]*\]'
        self.createDB()

    def set_item_info(self, item, results, **kwargs):
        """Contains the logic of the provider connection, and adds it to the Thread"""
        providerItem = self.getMoreInformation(item)
        mediatype = item.get('mediatype')
        if mediatype == 'movie':
            newItem = self.iterateItemMovie(providerItem)
        elif mediatype == 'tv':
            newItem = self.iterateItemShow(providerItem)
        elif mediatype == 'season':
            newItem = self.iterateItemSeason(providerItem)
        elif mediatype == 'episode':
            newItem = self.iterateItemEpisode(providerItem)
        else:
            raise Exception('Mediatype not specified')
        results.append(newItem)

    def set_itemlist_info(self, items, **kwargs):
        """Creates the required threads to parse Scrapper for each item"""
        results = list()
        threads = list()
        for index, item in list(enumerate(items)):
            thread = threading.Thread(
                target=self.set_item_info, args=(item, results), kwargs=kwargs)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        if len(results) == 1:
            return results[0]
        return results

    def createDB(self):
        if self.provider is None:
            raise Exception(
                "You must define the scrapper provider in the class")
        sqlSchema = '''CREATE TABLE IF NOT EXISTS "DATA_{}" (
            "url"	TEXT,
            "responseJson"	TEXT)'''.format(self.provider)
        databaseConnection = sqlite3.connect(DB_FILE)
        databaseConnection.execute(sqlSchema)
        databaseConnection.commit()
        databaseConnection.close()

    def insertTableSchema(self, **kwargs):
        sqlSchema = 'INSERT OR REPLACE INTO DATA_%s (%s) VALUES (%s)' % (
            self.provider,
            ', '.join(kwargs.keys()),
            ', '.join(['"%s"' % str(v).replace('"', "'")
                       for v in kwargs.values()])
        )
        self.commitSQL(sqlSchema)

    def checkInDatabase(self, url):
        """Check if the item is already in the DB, if exists returns the information"""
        sqlSchema = "SELECT * FROM DATA_{} WHERE url == '{}'".format(
            self.provider, url)
        return self.executeSQL(sqlSchema)

    def executeSQL(self, sql):
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        connection.close()
        return data

    def commitSQL(self, sql, dataSeq=None):
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        if dataSeq is not None:
            cursor.execute(sql, dataSeq)
        else:
            cursor.execute(sql)
        connection.commit()
        connection.close()
        return True

    def _request(self, method, url, params=None, payload=None, **kwargs):
        response = requests.request(
            method,
            url,
            params=params,
            data=json.dumps(payload) if payload else payload,
            headers=kwargs.get('headers',
                               {}), timeout=kwargs.get('timeout',
                                                       None)
        )
        return response.json()

    def _GET(self, path, params=None, **kwargs):
        database = self.checkInDatabase(path)
        if database:
            return json.loads(base64.b64decode(database[0][1]).decode('utf-8'))
        response = self._request('GET', path, params=params, **kwargs)
        self.insertTableSchema(
            url=path,
            responseJson=base64.b64encode(json.dumps(response).encode('utf-8')).decode('utf-8'))
        return response

    def _POST(self, path, params=None, payload=None, **kwargs):
        database = self.checkInDatabase(path)
        if database:
            return json.loads(base64.b64decode(database[0][2]).decode('utf-8'))
        response = self._request(
            'POST', path, params=params, payload=payload, **kwargs)
        self.insertTableSchema(
            url=path,
            responseJson=base64.b64encode(json.dumps(response).encode('utf-8')).decode('utf-8'))
        return response

    def iterateItemMovie(self, providerItem):
        """Converts the movie provider info into Kodi Item"""

    def iterateItemShow(self, providerItem):
        """Converts the show provider info into Kodi Item"""

    def iterateItemSeason(self, providerItem):
        """Converts the season tv show provider info into Kodi Item"""

    def iterateItemEpisode(self, providerItem):
        """Converts the episode tv show provider info into Kodi Item"""

    def get_videos(self, providerId, providerResults=None):
        """Get's the trailer from the provider"""


from .tmdb import TMDBScrapper
__all__ = ['LSPScrapper', 'TMDBScrapper']
