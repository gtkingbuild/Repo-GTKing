# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.vidcorn2.com/'


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone ( title = 'Españolas', action = 'list_all', url = host + 'search/label/Españolas', text_color='moccasin' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(host).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Peliculas<(.*?)</ul></li>')

    matches = scrapertools.find_multiple_matches(bloque, "<a href='(.*?)'>(.*?)</a>")

    for url, title in matches:
        if descartar_xxx:
            if title == 'Erótico': continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile("<div class='cards-movie'>(.*?)</div></div>", re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, " href='(.*?)'")

        title = scrapertools.find_single_match(match, " title='(.*?)'")
        if not title: title = scrapertools.find_single_match(match, '<h2>(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, " src='(.*?)'")

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year: year = '-'

        if ('(' + year + ')') in title: title = title.replace(('(' + year + ')'), '').strip()

        title = title.replace('&#39;', '"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<div class='paginacion'>.*?<a class='bton-paginacion bton-right'.*?href='(.*?)'")

        if next_page:
            if '?updated-max=' in next_page:
                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<IFRAME SRC="(.*?)"')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<iframe src="(.*?)"')

    ses = 0

    for enlace in matches:
        ses += 1

        url = enlace

        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if not servidor == 'directo':
            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Esp' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
