# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.tryboobs.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'most-popular/week/' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'top-rated/week/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url= host + 'categories/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'models/model-viewed/1/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a href="([^"]+)" class="th-[^"]+">.*?'
    patron += 'src="([^"]+)" alt=.*?'
    patron += '<span>(\d+)</span>.*?'
    patron += '<span class="title">([^"]+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, total, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='tan' ))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a href="([^"]+)" class="th-[^"]+">.*?'
    patron += 'src="([^"]+)" alt=.*?'
    patron += '<span>(\d+)</span>.*?'
    patron += '<span class="title">([^"]+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, total, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='moccasin' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li><a class="pag-next" href="([^"]+)"><ins>Next</ins></a>')

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'pornstars', url = next_url, text_color = 'coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = 'href="([^"]+)"\s*class="th-video.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<span class="time">([^"]+)</span>.*?'
    patron += '<span class="title">([^"]+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, duration, title in matches:
        title = "[COLOR tan]%s[/COLOR] %s" % (duration, title)

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li><a class="pag-next" href="([^"]+)"><ins>Next</ins></a>')

        if next_page:
            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    matches = scrapertools.find_multiple_matches(data, '<video src="([^"]+)"')

    for url in matches:
        url += '|Referer=' + host

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='directo', language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/?q=%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
