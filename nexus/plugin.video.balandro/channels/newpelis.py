# -*- coding: utf-8 -*-

import re, base64

from platformcode import logger, config
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://newpelis.re/'


# ~ Series NO pq no hay buscar


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://newpelis.org/']

    raise_weberror = False if '/year/' in url else True

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1993, -1):
        itemlist.append(item.clone( title=str(x), url= host + '/year/' + str(x) + '/', action='list_all', any = str(x), text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="short_header">(.*?)</div>').strip()

        if not url or not title: continue

        title = title.replace("&#8217;", "'")

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = '-'

        if item.any: year = item.any

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')

        if next_url:
            if '/page/' in next_url:
               itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'rel="noopener" href="(.*?)".*?">(.*?)</a>')

    for url, play_down in matches:
        if url == '#': continue

        new_url = item.url
        if play_down == 'descargar': new_url = new_url + '?download'
        else: new_url = new_url + '?play'

        data = do_downloadpage(new_url)

        if '<ul class="server-list">' in data:
            links = scrapertools.find_multiple_matches(data, '<li class="change-server(.*?)</li>')

            for link in links:
                url_link = scrapertools.find_single_match(link, 'data-id="(.*?)"')

                url_link = base64.b64decode(url_link).decode("utf-8")

                servidor = servertools.get_server_from_url(url_link)
                servidor = servertools.corregir_servidor(servidor)

                url_link = servertools.normalize_url(servidor, url_link)

                if servidor == 'youtube': continue

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                   if not config.get_setting('developer_mode', default=False): continue

                if not servidor == 'directo':
                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url_link, title = '', language = 'Lat' ))

        else:
            bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

            links = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

            for link in links:
                servidor = servertools.get_server_from_url(link)
                servidor = servertools.corregir_servidor(servidor)

                if servertools.is_server_available(servidor):
                    if not servertools.is_server_enabled(servidor): continue
                else:
                   if not config.get_setting('developer_mode', default=False): continue

                url_link = servertools.normalize_url(servidor, link)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url_link, title = '', language = 'Lat', other = 'D' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
       itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
       itemlist.append(item.clone(server = item.server, url = url))

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

