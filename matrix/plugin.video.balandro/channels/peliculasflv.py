# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.peliculasflv.io/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article>(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        if url.startswith('/'): url = host + url[1:]

        thumb = scrapertools.find_single_match(article, '<img src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()

        year = scrapertools.find_single_match(article, '<div class="year">(\d+)<')
        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="counter">.*?<a href="(.*?)"')
        if next_page:
            if '/pagina' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<div class="sub-items">(.*?)<div id="bottom">')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)')

    for url, title in matches:
        if url.startswith('/'): url = host + url[1:]

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return sorted(itemlist, key=lambda it: it.title)


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url) 
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    IDIOMAS = {'Latino': 'Lat', 'Español': 'Esp', 'Subtitulado': 'Vose'}

    bloque = scrapertools.find_single_match(data,'<section class="list" id="player">(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque,'<tr>(.*?)</tr>')

    ses = 0

    for match in matches:
        ses += 1

        servidor = scrapertools.find_single_match(match,'img src=".*?.*?/>\s.*?<span>(.*?)<').strip().lower()
        if not servidor: continue

        url = scrapertools.find_single_match(match,'href="(.*?)"')
        lang = scrapertools.find_single_match(match,'img src=.*?</span>.*?<td>(.*?)</td>').strip()
        qlty = scrapertools.find_single_match(match,'img src=.*?</td>.*?</td>.*?<td>(.*?)</td>').strip()

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, title = '',
                                  language = IDIOMAS.get(lang, lang), quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = ''

    if item.url.startswith(host):
        hash = item.url.replace(host + 'enlace/ver/', '').replace(host + 'enlace/descargar/', '')
        if hash.endswith("/"): hash = hash.replace('/', '')

        url_php = host + 'player.php?file=' + hash

        data = do_downloadpage(url_php)

        url = scrapertools.find_single_match(data, '<iframe src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, "<iframe src='(.*?)'")

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar/' + texto.replace(" ", "+") + '/'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
