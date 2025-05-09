# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2024 Someone Like You
#
# This file is part of Astro & Tacones.
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
# ----------------------------------------------------------------------

import requests
import os
import xbmcvfs
import xbmcgui
import xbmcaddon
import urllib.request
from xml.etree import ElementTree


ADDON = xbmcaddon.Addon()
TITLE = ADDON.getAddonInfo("name")
ICON = ADDON.getAddonInfo("icon")

HOME = xbmcvfs.translatePath(ADDON.getAddonInfo("Path"))
SP_HOME = xbmcvfs.translatePath("special://home/")
ADDONS_DIR = os.path.join(SP_HOME, "addons")
PACKAGES_DIR = os.path.join(xbmcvfs.translatePath(ADDONS_DIR), "packages")

if not os.path.exists(PACKAGES_DIR):
    os.makedirs(PACKAGES_DIR)


class DialogProgress(object):
    def __init__(self, header, silent=False, messages={}) -> None:
        self.dialog = xbmcgui.DialogProgress() if not silent else xbmcgui.DialogProgressBG()
        self.dialog.create(header, self.formatMessages(messages))
        self.canceled = False
        self.checkCanceled()
        if self.canceled:
            self.close()

    def checkCanceled(self):
        if isinstance(self.dialog, xbmcgui.DialogProgress):
            self.canceled = self.dialog.iscanceled()
        elif isinstance(self.dialog, xbmcgui.DialogProgressBG):
            self.canceled = self.dialog.isFinished()

    def update(self, percent, messages={}):
        self.dialog.update(percent,
                           self.formatMessages(messages))

    def formatMessages(self, messages):
        return "\n".join([message for key, message in messages.items()
                          if key.startswith("line")])

    def downloadPercentage(self, block_num, block_size, total_size, messages={}):
        percent = (block_num * block_size * 100) / total_size
        self.update(int(percent), messages)
        if percent > total_size:
            self.close()

    def close(self):
        self.dialog.close()


class Updater(object):
    """This class is used to check if the addon is updated, and if not, update it"""

    def __init__(self):
        self.RELEASES_URL = "https://api.github.com/repos/830NY/Tacones_Addon/releases?per_page=100&page=1"
        self.LOCAL_VERSION = None
        self.getLocalVersion()

    def getLocalVersion(self):
        """This function read the version from the addon.xml file"""
        with open(os.path.join(xbmcvfs.translatePath(HOME), "addon.xml"), 'r', encoding='utf-8') as addonXml:
            data = ElementTree.fromstring(addonXml.read())
            self.LOCAL_VERSION = data.get("version")

    def checkAvailableVersion(self, silent):
        releases = requests.get(self.RELEASES_URL).json()
        self.filtered_releases = list(filter(lambda rls: self.versiontuple(
            rls.get("tag_name")) > self.versiontuple(self.LOCAL_VERSION), releases))

        if len(self.filtered_releases) > 0:
            self.release = self.filtered_releases[0]
            self.downloadRemoteVersion(silent)
            return True
        else:
            return False

    def downloadRemoteVersion(self, silent):
        self.release_url = self.release.get(
            "assets")[0].get("browser_download_url", None)
        dest = os.path.join(PACKAGES_DIR, self.release_url.split('/')[-1])
        self.download_file(self.release_url, dest, silent)
        self.extract_file(dest, ADDONS_DIR, silent)
        xbmcgui.Dialog().notification(
            TITLE, "El addon se ha actualizado, es necesario que vuelva a abrir el addon", ICON)
        exit()

    def extract_file(self, in_dest, out_dest, silent):
        from zipfile import ZipFile
        dialog = DialogProgress(TITLE, silent)
        with ZipFile(in_dest, 'r') as zip_ref:
            nFiles = float(len(zip_ref.infolist()))
            count = 0
            for item in zip_ref.infolist():
                count += 1
                update = count / nFiles * 100
                dialog.update(int(update), {"line1": f"Extrayendo {TITLE}..."})
                zip_ref.extract(item, out_dest)

    def download_file(self, url, dest, silent):
        dialog = DialogProgress(TITLE, silent)
        urllib.request.urlretrieve(
            url, dest, lambda nb, bs, fs: dialog.downloadPercentage(nb, bs, fs, {"line1": f"Descargando {TITLE}..."}))

    def versiontuple(self, vrs):
        """https://stackoverflow.com/a/11887825"""
        return tuple(map(int, (vrs.split("."))))
