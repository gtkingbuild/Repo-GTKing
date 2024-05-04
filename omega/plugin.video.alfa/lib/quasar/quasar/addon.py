# -*- coding: utf-8 -*-
import os
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
if not PY3:
    ADDON_ICON = ADDON.getAddonInfo("icon").decode('utf-8')
    try:
        ADDON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__).decode(sys.getfilesystemencoding(), 'ignore')), "..", "..", ".."))
    except:
        ADDON_PATH = ADDON.getAddonInfo("path").decode('utf-8')
else:
    ADDON_ICON = ADDON.getAddonInfo("icon")
    try:
        ADDON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".."))
    except:
        ADDON_PATH = ADDON.getAddonInfo("path")
