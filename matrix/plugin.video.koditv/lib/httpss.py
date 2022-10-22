def main():
    import os
    import sys
    import urllib.request, urllib.parse, urllib.error
    import urllib.request, urllib.error, urllib.parse
    import re
    import xbmc
    import xbmcgui
    import xbmcaddon
    import xbmcplugin
    import plugintools
    import unicodedata
    import base64
    import requests
    import shutil
    import base64
    import time
    try:
        my_kodi = xbmc.translatePath('special://home/userdata/favourites.xml')
        f = open (my_kodi,'r')
        diainfo = f.read()
        data = plugintools.find_multiple_matches(diainfo,'<favourite name=".*?plugin.video.koditv.*?</favourite>')   
        for generos in data:
            mac=plugintools.find_single_match( generos,'plugin.video.koditv(.*?)</favourite>') 
            for mac in mac:            
                diainfo1=mac.replace(mac,'caca')
                f = open(my_kodi,'w+')
                f.write(diainfo1)
                f.close()
                    
    except:
        pass