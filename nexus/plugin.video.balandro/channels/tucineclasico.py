# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://online.tucineclasico.es/'


perpage = 25


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/?get=movies' ))

    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies' ))
    itemlist.append(item.clone ( title = 'Más valoradas', action = 'list_all', url = host + '22-2/?get=movies' ))

    itemlist.append(item.clone ( title = 'Subtitulado', action = 'list_all', url = host + 'genero/version-original-subtitulada/?get=movies' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)')
    for url, title in matches:
        if 'genero/version-original-subtitulada' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return sorted(itemlist, key = lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<nav class="releases">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    for ano in range(1948, 1921, -1):
        itemlist.append(item.clone( action = 'list_all', title = str(ano), url = host + 'lanzamiento/' + str(ano) + '/', text_color = 'deepskyblue' ))

    return sorted(itemlist, key = lambda it: it.title, reverse=True)


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    if '/peliculas/' in item.url:
        if '<h2>' in data: data = data.split('<h2>')[1] # descartar destacadas
        if '<div class="dt_mainmeta">' in data: data = data.split('<div class="dt_mainmeta">')[0] # descartar más vistas

    elif '/lanzamiento/' in item.url:
        if '>Mas Populares</h2>' in data: data = data.split('>Mas Populares</h2>')[0] # descartar mas populares

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h4>(.*?)</h4>')
        if not title: title = scrapertools.find_single_match(article, ' alt="([^"]+)"')

        if not url or not title: continue

        title = title.replace('&#8230;', '')

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year: year = '-'

        if ('(' + year + ')') in title: title = title.replace(('(' + year + ')'), '')

        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="fas fa-chevron-right">')

            if next_page:
                itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def get_url(dpost, dnume, dtype, referer):
    logger.info()
    itemlist = []

    post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}
    data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':referer}, raise_weberror=False).data

    url = scrapertools.find_single_match(data, "(?i) src=.*?'([^']+)")
    if not url: url = scrapertools.find_single_match(data, '(?i) src=.*?"([^"]+)')

    return url


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'mx': 'Lat', 'en': 'Vose'}

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, "<ul id='playeroptionsul'(.*?)</ul>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(\d+)'(.*?)</li>")

    for optnum, enlace in matches:
        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        dtype = scrapertools.find_single_match(enlace, "data-type='([^']+)")
        dpost = scrapertools.find_single_match(enlace, "data-post='([^']+)")
        dnume = scrapertools.find_single_match(enlace, "data-nume='([^']+)")

        if not dtype or not dpost or not dnume or dnume == 'trailer': continue

        url = get_url(dpost, dnume, dtype, item.url)
        url = url.replace('\\/', '/')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if not servidor or servidor == 'directo': continue

            url = servertools.normalize_url(servidor, url)

            if '\\' in url: url = url.replace('\\', '/')

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')

        if ('(' + year + ')') in title: title = title.replace(('(' + year + ')'), '')

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        langs = []
        if 'img/flags/es.png' in article: langs.append('Esp')
        if 'img/flags/mx.png' in article: langs.append('Lat')
        if 'img/flags/en.png' in article: langs.append('Vose')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs), contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_search', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)"[^>]*><span class="fas fa-chevron-right">')

            if next_page_link:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page_link, page = 0, action='list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
