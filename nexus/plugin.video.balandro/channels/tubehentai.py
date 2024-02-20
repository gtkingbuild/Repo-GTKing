# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://tubehentai.com/'

perpage = 30


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'most-recent/'))

    itemlist.append(item.clone( title = 'Al azar', action = 'list_all', url = host + 'random/'))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'most-viewed/'))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'top-rated/'))
    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + 'longest/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias'))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'channels/').data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="videobox.*?<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)"').findall(data)

    for url, thumb, title in matches:
        if title == 'Photos': continue

        title = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb, text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="putvideo">(.*?)</div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        duration = scrapertools.find_single_match(match, '<div class="text-pink border border-pink px-2">(.*?)$')

        titulo = "[COLOR tan]%s[/COLOR] %s" % (duration, title)
                             
        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<a href=\'([^\']+)\' class="next"')
        if next_page:
            next_page = host + next_page

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<source src="([^"]+\.mp4)"')
    if not url: url = scrapertools.find_single_match(data, '<div class="videohere".*?src="([^"]+)"')

    if url:
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = 'Vo' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "search/videos/%s/" % (texto.replace(" ", "-"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
