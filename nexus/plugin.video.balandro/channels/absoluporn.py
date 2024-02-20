# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'http://www.absoluporn.com'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host  + '/en/wall-date-1.html' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host  + '/en/wall-main-1.html' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host  + '/en/wall-note-1.html' ))
    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host  + '/en/wall-time-1.html' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + '/en' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron  = '&nbsp;<a href="([^"]+)" class="link1b">([^"]+)</a>&nbsp;<span class="text23">([^<]+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, title, cantidad in matches:
        titulo = '[COLOR orange]%s[/COLOR] %s' % (title, cantidad)

        url = url.replace('..', '')

        url = url.replace('.html', '_date.html')

        url = host + url

        itemlist.append(item.clone (action='list_all', title=titulo, url=url, text_color = 'tan' ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    patron = '<div class="thumb-main-titre"><a href="([^"]+)".*?title="([^"]+)".*?src="([^"]+)".*?<div class="time">(.*?)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, title, thumb, time in matches:
        url = url.replace('..', '')

        url = host + url

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="text16">\d+</span> <a href="..([^"]+)"')

        if next_page:
            next_page = host + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    patron  = 'servervideo = \'([^\']+)\'.*?path = \'([^\']+)\'.*?filee = \'([^\']+)\'.*?'

    matches = scrapertools.find_multiple_matches(data, patron)

    for servervideo, path, filee  in matches:
        url = "%s%s56ea912c4df934c216c352fa8d623af3%s" % (servervideo, path, filee)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server = servidor, language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '/search-%s-1.html' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
