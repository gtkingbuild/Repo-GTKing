# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://jizzbunker.com/en/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'newest/' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'straight/popular1/' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'straight/trending/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url= host + 'channels/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron  = '<li><figure>.*?<a href="([^"]+)".*?'
    patron += '<img class="lazy" data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="score">(\d+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, title, total in matches:
        url = url.replace('channel', 'channel30')

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='tan' ))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron  = '<li><figure>.*?<a href="([^"]+)".*?'
    patron += '<img class="lazy" data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<time datetime=".*?">([^"]+)</time>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, title, duration, in matches:
        title = "[COLOR tan]%s[/COLOR] %s" % (duration, title)

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)" rel="next">&rarr;</a>')

        if next_page:
            if not host in next_page:
                next_page = host + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = scrapertools.find_multiple_matches(data, 'type:\'video/mp4\',src:\'([^\']+)\'')

    for url in matches:
        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='directo', language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search?query=%s/' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
