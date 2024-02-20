# -*- coding: utf-8 -*-

import re


from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://documentaryheaven.com/'


def mainlist(item):
    logger.info()
    itemlist = []

    # ~ reCaptcha
    # ~ itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'all'))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Categories<(.*?)</aside>')

    matches = scrapertools.find_multiple_matches(bloque, 'href=(.*?) title=.*?">(.*?)</a>')

    for url, title in matches:
        url = url.strip()

        url = host[:-1] + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color='cyan' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href=(.*?) title=')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        url = url.strip()

        thumb = scrapertools.find_single_match(match, 'src=(.*?) class="')

        thumb = thumb.strip()

        thumb = host[:-1] + thumb

        plot = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        title = title.replace('&#8217;', "'")

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, plot = plot,
                                    contentType='movie', infoLabels={"year": '-', "plot": plot}, contentTitle=title, contentExtra='documentary' ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class=active>.*?</a>.*?href=(.*?)>')

        next_page = next_page.strip()

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, 'itemprop="embedUrl" content="(.*?)"')

    if url:
        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = 'Vo' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'find/?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
