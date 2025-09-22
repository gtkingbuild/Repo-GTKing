# -*- coding: utf-8 -*-
import sys
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui
try:
    # Python 3
    from urllib.parse import parse_qsl
except ImportError:
    # Python 2
    from urlparse import parse_qsl

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
handle = int(sys.argv[1])

def add_list_item(name, url, is_folder):
    li = xbmcgui.ListItem(label=name)
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=is_folder)

def main():
    add_list_item("{0}: {1}".format(addon_name, addon_version), "", False)
    add_list_item("Alterar configuração", "plugin://{0}/?action=settings".format(addon_id), False)
    xbmcplugin.endOfDirectory(handle)

if __name__ == "__main__":
    params = dict(parse_qsl(sys.argv[2][1:]))
    action = params.get('action')
    if not action:
        main()
    elif action == "settings":
        addon.openSettings()