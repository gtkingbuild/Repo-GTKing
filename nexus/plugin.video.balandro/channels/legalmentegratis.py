# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'http://legalmentegratis.com/'


web_otros = [
   ('alfred-hitchcock'),
   ('anitra-ford'),
   ('bela-lugosi'),
   ('buster-keaton'),
   ('cary-grant'),
   ('david-lynch'),
   ('ed-wood'),
   ('eisenstein'),
   ('frank-capra'),
   ('frank-sinatra'),
   ('fritz-lang'),
   ('gary-cooper'),
   ('george-romero'),
   ('griffith'),
   ('henry-mancini'),
   ('murnau'),
   ('orson-welles'),
   ('roger-corman'),
   ('tarantino'),
   ('tarkovski'),
   ('vincent-price')
   ]


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por dirección, interprete', action = 'otros', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    matches = [
        ['cienciaficcion/', 'Ciencia Ficción'],
        ['comedia/', 'Comedia'],
        ['documental/', 'Documental'],
        ['drama/', 'Drama'],
        ['ecologia/', 'Ecología'],
        ['erotismo/', 'Erotismo'],
        ['gore/', 'Gore'],
        ['policial/', 'Policial'],
        ['romantica/', 'Romántica'],
        ['surrealismo/', 'Surrealismo'],
        ['suspenso/', 'Suspenso'],
        ['terror/', 'Terror'],
        ['thriller/', 'Thriller'],
        ['vampiros/', 'Vampiros'],
        ['/western/', 'Western'],
        ['zombies/', 'Zombies']
        ]

    for url, title in matches:
        if descartar_xxx:
            if title == 'Erotismo': continue

        url = host + 'category/' + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url = host + 'eco/'

    data = httptools.downloadpage(url).data

    bloque = scrapertools.find_single_match(data, '<span>Etiquetas</span>(.*?)</aside>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?aria-label.*?">(.*?)</a>')

    for url, title in matches:
        despreciar = url.replace(host, '').replace('tag/', '').replace('/', '')
        if despreciar in web_otros: continue

        itemlist.append(item.clone( title = title.capitalize(), url = url, action = 'list_all', text_color='moccasin' ))

    return sorted(itemlist, key = lambda it: it.title)


def otros(item):
    logger.info()
    itemlist = []

    for x in web_otros:
        title = str(x)

        title = title.replace('-', ' ').capitalize()

        url = host + 'tag/' + str(x) + '/'

        itemlist.append(item.clone( title = title, url = url, action = 'list_all', text_color='tan' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(match, 'rel="bookmark">(.*?)</a>')

        if not url or not title: continue

        title = title.replace('Poster', '').replace('pelicula', '').replace('película', '').replace('online', '').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        plot = scrapertools.find_single_match(match, "<p>(.*?)</p>")

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, infoLabels={'year': '-', 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="nav-previous"><a href="(.*?)"')

        if next_page:
            itemlist.append(item.clone(action = 'list_all', title = 'Siguientes ...', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    idioma = scrapertools.find_single_match(data, '<p><strong>(.*?)</strong>').lower()

    if 'subtitul' in idioma: lang = 'Vose'
    elif 'n original' in idioma: lang = 'VO'
    else: lang = 'Esp'

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    ses = 0

    for url in matches:
        ses += 1

        if url.startswith('//'): url = 'https:' + url
        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, title = '', language = lang)) 

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+") + '&submit=Search'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
