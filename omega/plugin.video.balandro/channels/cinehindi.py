# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cinehindi.com/'


def do_downloadpage(url, post=None, headers=None):
    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estreno/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if not '>Películas Aleatorias<' in data:
       bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Más Populares<')
    else:
       bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Películas Aleatorias<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="navigation pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link".*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    lang = 'Vose'

    matches = re.compile('<div id="options-(.*?)"(.*?)</div>', re.DOTALL).findall(data)

    ses = 0

    for opt, match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, '<iframe src="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, '<iframe data-src="(.*?)"')

        if not url: continue

        other = scrapertools.find_single_match(data, 'href="#options-' + str(opt) + '.*?<span class="server">(.*?)</span>')

        other = other.replace('-Subtitulado', '').strip()

        srv = other.lower().strip()

        if other == 'hqq': continue

        servidor = servertools.corregir_servidor(srv)

        other = srv

        if servidor == srv: other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = servidor, language = lang, other = other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&')

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="([^"]+)')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

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
