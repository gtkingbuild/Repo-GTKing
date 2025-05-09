# -*- coding: utf-8 -*-
from lib.helper import *
try:
    from lib.ClientScraper import cfscraper
except ImportError:
    from ClientScraper import cfscraper


def radios_list(API):
    try:
        radios = cfscraper.get(API).json()
        setcontent('music')
        fanart = 'https://conteudo.imguol.com.br/c/entretenimento/4f/2017/11/24/mulher-ouvindo-musica-1511535013801_v2_4x3.jpg'
        for i in radios:
            name = i['name']
            iconimage = i['logo']
            stream = i['stream']
            li = xbmcgui.ListItem(name)
            li.setProperty('IsPlayable', 'true')
            li.setArt({"icon": "DefaultVideo.png", "thumb": iconimage})
            if kversion > 19:
                info = li.getVideoInfoTag()
                info.setMediaType('music')
            else:
                li.setInfo('music', {'mediatype': 'song'})
            li.setProperty('fanart_image', fanart)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=stream, listitem=li, isFolder=False)
        end()            
    except:
        pass
