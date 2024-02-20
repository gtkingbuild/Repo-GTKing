# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://mega1link.com/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action='list_all', url = host + 'peliculas/' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Castellano', action='list_all', url = host + 'tag/espanol-castellano/', text_color='moccasin' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url = host + 'tag/espanol-latino/', text_color='moccasin' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url = host + 'tag/subtitulada/', text_color='moccasin' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Genero</a>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        if '/genero/' not in url: continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    if itemlist:
        itemlist.append(item.clone( action = 'list_all', title = 'Bélica', url = host + 'genero/belica/', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'genero/western/', text_color = 'deepskyblue' ))

    return sorted(itemlist, key=lambda it: it.title)


def calidades(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, 'Calidad</a>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')
    if not matches: matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title='En ' + title, url = url, text_color='moccasin' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)<strong>Mega1Link</strong>')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1>(.*?)<strong>Mega1Link</strong>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        article = scrapertools.decodeHtmlentities(article)

        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, " href='(.*?)'")
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' data-src=(.*?) ')

        year = scrapertools.find_single_match(article, '<span class=year>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>.*?,(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span>(.*?)</span>').strip()

        if year: title = title = title.replace(' ' + year, '').replace(' (' + year + ')', '').strip()
        else: year = '-'

        qlty = scrapertools.find_single_match(article, '<span class=quality>(.*?)</span>')
        qlty = re.sub(' -$', '', qlty)

        plot = scrapertools.find_single_match(article, '<div class=texto>(.*?)</div>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "<a href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral'))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['tscam', 'brscreener', 'dvdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español Castellano': 'Esp', 'Español Latino': 'Lat', 'Subtitulada': 'Vose'}

    data = httptools.downloadpage(item.url).data

    # Enlaces en descargas
    matches = re.compile('<tr id=(.*?)</tr>', re.DOTALL).findall(data)

    ses = 0

    for lin in matches:
        ses += 1

        if '<th' in lin: continue

        url = scrapertools.find_single_match(lin, '<a href="(.*?)"')
        if not url: url = scrapertools.find_single_match(lin, "<a href='(.*?)'")

        server = servertools.corregir_servidor(scrapertools.find_single_match(lin, "domain=([^.']+)"))

        if not url or not server: continue

        if server == 'soon': continue

        if servertools.is_server_available(server):
            if not servertools.is_server_enabled(server): continue
        else:
            if not config.get_setting('developer_mode', default=False): continue

        if url.startswith('//'): url = 'https:' + url

        qlty = scrapertools.find_single_match(lin, '<strong class=quality>(.*?)</strong>').replace('mp4', '').strip()

        lang = scrapertools.find_single_match(lin, "<td>([^<]+)")

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(host):
        data = httptools.downloadpage(item.url).data

        url = scrapertools.find_single_match(data, '<a id=.*?href="(.*?)"')

        if url:
            if 'url=' in url: url = scrapertools.find_single_match(url, 'url=(.*?)$')

            url = url.replace('&amp;', '&')

            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                if servidor and servidor != 'directo':
                    url = servertools.normalize_url(servidor, url)
                    itemlist.append(item.clone( url=url, server=servidor ))
    else:
        itemlist.append(item.clone())

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)<strong>Mega1Link</strong>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        article = scrapertools.decodeHtmlentities(article)

        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        if not url: url = scrapertools.find_single_match(article, " href='(.*?)'")
        if not url: url = scrapertools.find_single_match(article, ' href=(.*?)>')

        title = scrapertools.find_single_match(article, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' data-src=(.*?) ')

        year = scrapertools.find_single_match(article, '<span class=year>(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>.*?,(.*?)</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span>(.*?)</span>').strip()

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if year: title = title = title.replace(' ' + year, '').replace(' (' + year + ')', '').strip()
        else: year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, ' href="([^"]+)"[^>]*><span class="icon-chevron-right">')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
