# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import os, re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


# ~ las Series todos los links NO son validos

host = 'https://www.vivatorrents.org/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    data = httptools.downloadpage(url, post=post, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos/', search_type = 'movie', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + '?orderby=relevance', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<div id="categories-(.*?)</aside>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for genre, title in matches:
        if title == 'Estrenos': continue

        title = title.replace('Ciencia ficciÃ³n', 'Ciencia Ficción').replace('FantasÃ­a', 'Fantasia')

        itemlist.append(item.clone( action = 'list_all', title = title, url = genre, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()
        if not title: title = scrapertools.find_single_match(match, '<h2 class="Title"(.*?)</h2>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<i>(.*?)</i>')
        if not year: year = '-'

        qlty = ''
        if '(720p)' in title:
            qlty = '720p'
            title = title.replace('(720p)', '').strip()
        elif '(1080p)' in title:
            qlty = '1080p'
            title = title.replace('(1080p)', '').strip()
        elif '(DVDrip)' in title:
            qlty = 'DVDrip'
            title = title.replace('(DVDrip)', '').strip()
        elif '(BRS)' in title:
            qlty = 'BRS'
            title = title.replace('(BRS)', '').strip()
        elif '(HDRip)' in title:
            qlty = 'HDRip'
            title = title.replace('(HDRip)', '').strip()
        elif '(HDR)' in title:
            qlty = 'HDR'
            title = title.replace('(HDR)', '').strip()
        elif '(TS)' in title:
            qlty = 'TS'
            title = title.replace('(TS)', '').strip()
        elif '3D' in title:
            qlty = '3D'
            title = title.replace('3D', '').strip()

        title = title.replace('Español Torrent', '').strip()

        tipo = 'movie' if '/movies/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            titulo = title.replace('&#8211;', 'T:').replace('&#215;', 'E:')
            temp = scrapertools.find_single_match(titulo, "T:(.*?)E:").strip()
            epis = scrapertools.find_single_match(titulo, "E:(.*?)$").strip()

            if not temp or not epis: continue

            SerieName = scrapertools.find_single_match(titulo, "(.*?)T:").strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentSerieName = SerieName, contentType = 'episode', contentSeason = temp, contentEpisodeNumber = epis, infoLabels={'year': year} ))

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            titulo = title

            if "(" in titulo: titulo = titulo.split("(")[0]
            elif "[" in titulo: titulo = titulo.split("[")[0]

            if "Torrent" in titulo: titulo = titulo.split("Torrent")[0]

            titulo = titulo.strip()

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': year} ))


    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination".*?class="page-numbers current">.*?.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<span class="Num">(.*?)</span>.*?".*?data-url="(.*?)".*?data-lmt="(.*?)"')

    ses = 0

    for num, data_url, data_lmt in links:
        ses += 1

        url = base64.b64decode(data_url).decode("utf-8")

        itemlist.append(Item( channel = item.channel, action='play', title='', url=url, server='torrent', language='Esp' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '/?trdownload=' in url:
        if PY3:
            from core import requeststools
            data = requeststools.read(url, 'vivatorrents')
        else:
             data = do_downloadpage(url, raise_weberror=False)

        if data:
            if 'Página no encontrada' in str(data) or 'no encontrada</title>' in str(data) or '<h1>403 Forbidden</h1>' in str(data):
                 return 'Archivo [COLOR red]No encontrado[/COLOR]'

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

            return itemlist

        else: url = ''

    if url:
        if url.startswith('magnet:'):
            itemlist.append(item.clone( url = url, server = 'torrent' ))

        elif url.endswith(".torrent"):
            itemlist.append(item.clone( url = url, server = 'torrent' ))

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
