# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools


host = 'https://www.pornburst.xxx/'


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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', search_video = 'adult', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por canal', action = 'categorias', url = host + 'sites/' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'categories/', group = 'cats' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'categorias', url = host + 'pornstars/', group = 'stars' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    if item.group == 'cats': text_color = 'moccasin'
    elif item.group == 'stars': text_color = 'orange'
    else: text_color = 'violet'

    matches = re.compile('<div class="muestra-escena(.*?)<div class="clear">', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<a class="muestra-escena(.*?)</a>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        thumb = thumb.replace('/model2-', '/model')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        title = title.replace('&#039;', "'")

        title = title.capitalize()

        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb, text_color=text_color ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

        if next_page:
            if '/page' in next_page:
                itemlist.append(item.clone (action='categorias', title='Siguientes ...', url=next_page, text_color = 'coral') )

    if item.group == 'cats':
        return sorted(itemlist,key=lambda x: x.title)

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div class="box-link-productora">(.*?)</a></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        title = scrapertools.find_single_match(match, 'data-stats-video-name="(.*?)"')

        title = title.replace('&#039;', "'")

        time = scrapertools.find_single_match(match, '<span class="minutos">.*?</span>(.*?)</span>').strip()

        titulo = "[COLOR tan]%s[/COLOR] %s" % (time, title)

        itemlist.append(item.clone (action='findvideos', title=titulo, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title, contentExtra='adults') )

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="pagination_item pagination_item--next "><a href="(.*?)"')

        if next_page:
            if '/page' in next_page:
                next_page = host[:-1] + next_page

                itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = scrapertools.find_multiple_matches(data, '<source src="(.*?)"')

    for url in matches:
        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='directo', language = 'Vo') )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        config.set_setting('search_last_video', texto)

        item.url =  host + 'search/?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
