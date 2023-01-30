# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://torrentsdepeliculas.org/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/year/' in url:
        url = url.replace('/year/', '/')
        raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    # ~ Pelis 4K y las Series todos los links NO son validos
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1979, -1):
        url = host + 'year/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all', group = 'anio' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<header class="article__header">(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, 'rel="tag">(.*?)</a>')
        year = year.replace('Documentales', '').strip()
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span aria-current="page" class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<a  class="pixcode.*?href="(.*?)"')

    tot_links = len(links)

    ses = 0

    for url in links:
        ses += 1

        if url.startswith('magnet:'): pass
        elif url.endswith(".torrent"): pass
        else: continue

        other = ''
        if tot_links > 1: other = str(ses)

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='torrent', language='Esp', other=other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
