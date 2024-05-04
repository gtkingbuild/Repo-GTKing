# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

if PY3:
    import urllib.parse as urlparse
else:
    import urlparse


import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www.ecartelera.com/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar tráiler ...', action = 'search', search_type = 'movie', text_color = 'darkgoldenrod' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'videos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + 'peliculas/', search_type = 'movie', text_color = 'cyan' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="item isvideo"(.*?)</div></div>', re.DOTALL).findall(data)
    if not matches: matches = re.compile('<div class="mlist-item"(.*?)</div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, "href='(.*?)'")

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        duration = scrapertools.find_single_match(match, '<span class="length">(.*?)</span>')

        title = title.replace('&#039;', '').replace('&quot;', '').replace('&amp;', '').strip()

        titulo = '[COLOR tan]' + duration + '[/COLOR] ' + title

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, thumbnail = thumb, search_type = 'movie' ))

    if itemlist:
        matches = re.compile('<a href="([^"]+)">Siguiente</a>', re.DOTALL).findall(data)

        for url in matches:
            itemlist.append(item.clone( title = 'Siguientes ...', url = url, action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if '/peliculas/' in item.url:
        new_url = scrapertools.find_single_match(data, '<div class="pel-trailer"><a href="(.*?)"')

        if new_url: data = httptools.downloadpage(new_url).data

    matches = re.compile('<source src="([^"]+)"', re.DOTALL).findall(data)

    if not matches:
        new_url = scrapertools.find_single_match(data, '</table>.*?<a href="(.*?)"')

        if new_url:
            data = httptools.downloadpage(new_url).data

            matches = re.compile('<source src="([^"]+)"', re.DOTALL).findall(data)

    for url in matches:
        url = urlparse.urljoin(item.url, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = 'VO' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    post = {'q': item.tex, 'tab': 'resumen'}

    data = httptools.downloadpage(host + 'ajax/_typesense/', post = post, headers = {'Referer': host + 'buscar/?q=' + item.tex}).data

    matches = scrapertools.find_multiple_matches(str(data), '"adicionales":(.*?)"coincidencia":')

    for match in matches:
        if not '"PELI"' in match: continue

        url = scrapertools.find_single_match(str(match), '"url".*?"(.*?)"')

        title = scrapertools.find_single_match(str(match), '"titulos":.*?"(.*?)"')

        if not url or not title: continue

        url = host + '/peliculas/' + url

        itemlist.append(item.clone( action='findvideos', url=url, title=title, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.tex = texto.replace(" ", "+")
       return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

