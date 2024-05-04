# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://zbporn.com/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'latest-updates/' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'most-popular/' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'top-rated/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url= host + 'categories/' ))
    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url= host + 'channels/' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'performers/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)>Recommended<')

    matches = re.compile('<div class="th".*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"', re.DOTALL).findall(bloque)

    for url, title, thumb in matches:
         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color='tan' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)>Recommended<')

    matches = re.compile('<div class="th".*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"', re.DOTALL).findall(bloque)

    for url, title, thumb in matches:
         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, tipo = 'canales', text_color='orange' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-current"><span class="item">.*?href="(.*?)"')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='canales', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)>Recommended<')

    matches = re.compile('<div class="th".*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"', re.DOTALL).findall(bloque)

    for url, title, thumb in matches:
         itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, tipo = 'pornstars', text_color='moccasin' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-current"><span class="item">.*?href="(.*?)"')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='pornstars', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if item.tipo == 'canales' or item.tipo == 'pornstars':
        if '<div class="comments-holder"' in data: bloque = scrapertools.find_single_match(data, '<h1>(.*?)<div class="comments-holder"')
        elif '<ul class="pagination-holder">' in data:  bloque = scrapertools.find_single_match(data, '<h1>(.*?)<ul class="pagination-holder">')
        else: bloque = scrapertools.find_single_match(data, '<h1>(.*?)</div></div></div></div>')
    else:
        bloque = scrapertools.find_single_match(data, '<h1>(.*?)</div></div></div></div>')

    if not bloque: bloque = scrapertools.find_single_match(data, '<h2>(.*?)</div></div></div></div>')

    matches = re.compile('<div class="th-image">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?<span class="th-duration">(.*?)</span>', re.DOTALL).findall(bloque)

    for url, title, thumb, duration, in matches:
        title = "[COLOR tan]%s[/COLOR] %s" % (duration, title)

        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="page-current"><span class="item">.*?href="(.*?)"')

        if next_page:
            next_page = host[:-1] + next_page

            itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    videos1 = scrapertools.find_multiple_matches(data, "video_url: '(.*?)'.*?video_url_text: '(.*?)'")

    videos2 = scrapertools.find_multiple_matches(data, "video_alt_url: '(.*?)'.*?video_alt_url_text: '(.*?)'")

    videos = videos1 + videos2

    for url, qlty in videos:
        qlty = qlty.replace('High Quality', 'HQ')

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='directo', quality = qlty, language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/%s/' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
