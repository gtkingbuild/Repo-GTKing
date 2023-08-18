# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://cineasiaenlinea.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/category/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'archivos/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Estrenos', action = 'list_all', url = host + 'archivos/estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Subtituladas', action = 'list_all', url = host + 'lenguaje/subtitulado/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por país', action = 'paises', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Peliculas por País<(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title=.*?">(.*?)</a>')

    for url, tit in matches:
        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Peliculas por genero<(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?title=.*?">(.*?)</a>')

    for url, tit in matches:
        itemlist.append(item.clone( title = tit, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Peliculas por Año<(.*?)</div>')
    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)"')

    for anio in matches:
        url = host + 'fecha-estreno/' + anio + '/'

        itemlist.append(item.clone( title = anio, url = url, action = 'list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<h3><a href="([^"]+)">([^<]+)<.*?src="([^"]+)".*?<a rel="tag">(.*?)<.*?<a rel="tag">(.*?)<'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, thumb, year, qlty in matches:
        title = re.sub(r' \((\d{4})\)$', '', title)

        title = title.replace("&#8217;", "'")

        if not year: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)"')

        if next_page:
            itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose', 'Subitulado': 'Vose'}

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<ul class="tabs">(.*?)<div id="clear">')

    matches = scrapertools.find_multiple_matches(bloque, '<div id="tab.*?src="(.*?)"')

    lang = scrapertools.find_single_match(data, '<p>Idioma.*?href=.*?rel="tag">(.*?)</a>').capitalize()

    ses = 0

    for url in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif '/gounlimited' in url: continue
        elif '/oogly.' in url: continue

        idioma = IDIOMAS.get(lang, lang)

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if '/streamhub.' in url: other = 'Streamhub'
        else: other = ''

        if servidor == 'zplayer': url += "|referer=%s" % host

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = idioma, other = other ))

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
