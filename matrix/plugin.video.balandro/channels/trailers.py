# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    import urllib.parse as urlparse
else:
    import urlparse


import re


from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = "https://www.ecartelera.com/"


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar tráiler ...', action = 'search', search_type = 'movie', text_color = 'darkgoldenrod' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'videos/', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="viditem"[^<]+'
    patron += '<div class="fimg"><a href="([^"]+)"><img alt="([^"]+)"\s*src="([^"]+)"\s*/><p class="length">([^<]+)</p></a></div[^<]+'
    patron += '<div class="fcnt"[^<]+'
    patron += '<h4><a[^<]+</a></h4[^<]+'
    patron += '<p class="desc">([^<]+)</p>'
    
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb, duration, plot in matches:
        title = scrapertools.htmlclean(title)

        titulo = '[COLOR tan]' + duration + '[/COLOR] ' + title

        thumb = re.sub('/(\d+)_th.jpg', '/f\\1.jpg', thumb)

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, thumbnail = thumb, search_type = 'movie',
                                    contentTitle = title, infoLabels = {'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        matches = re.compile('<a href="([^"]+)">Siguiente</a>', re.DOTALL).findall(data)

        for url in matches:
            itemlist.append(item.clone( title = 'Siguientes ...', url = url, action = 'list_all', text_color='coral' ))


    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<source src="([^"]+)"', re.DOTALL).findall(data)

    if not matches:
        new_url = scrapertools.find_single_match(data, '</table>.*?<a href="(.*?)"')

        if new_url:
            data = httptools.downloadpage(new_url).data

            matches = re.compile('<source src="([^"]+)"', re.DOTALL).findall(data)

    for url in matches:
        url = urlparse.urljoin(item.url, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="fl-item">(.*?)</a></p>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        if thumb.startswith('/'): thumb = host[:-1] + thumb

        year = scrapertools.find_single_match(match, '<p class="year"><span>(.*?)</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'buscar/?q=' + texto.replace(" ", "+")
       return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
