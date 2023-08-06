# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://pctmix1.live/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release-year/' in url: raise_weberror = False

    headers = {'Referer': host}
   
    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = {
        'action': 'Acción',
        'animation': 'Animación',
        'adventure': 'Aventura',
        'biography': 'Biografía',
        'sci-fi': 'Ciencia ficción',
        'comedy': 'Comedia',
        'crime': 'Crimen',
        'documentary': 'Documental',
        'drama': 'Drama',
        'family': 'Familia',
        'fantasy': 'Fantasía',
        'history': 'Historia',
        'horror': 'Horror',
        'music': 'Música',
        'romance': 'Romance',
        'sport': 'Deporte',
        'thriller': 'Thriller',
        'war': 'Guerra',
        'western': 'Western'
        }

    for opc in sorted(opciones):
        itemlist.append(item.clone( title = opciones[opc], url = host + 'genre/' + opc + '/', action ='list_all', text_color = 'deepskyblue' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'release-year/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div data-movie-id="(.*?)</div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(http[^"]+)')

        year = scrapertools.find_single_match(match, '<div class="jt-info">.*?>(.*?)</a>')

        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        title = title.replace("&#8217;", "'").replace("&#8211;", "").replace("&#038;", "")

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<link rel="next" href="' in data:
            next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')
        else:
            next_page = scrapertools.find_single_match(data, "<li class='active'>.*?</a>.*?href='(.*?)'")

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="btn-group btn-group-justified embed-selector" >(.*?)</div></div></div>')

    matches = re.compile('<a href="(.*?)".*?class="flag flag-(.*?)".*?<span class="lnk lnk-dl" >WEB(.*?)</span>', re.DOTALL).findall(bloque)

    for url, lang, qlty in matches:
        qlty = qlty.strip()

        if lang == 'us': lang = 'Vos'

        other = ''
        if 'magnet' in url: other = 'magnet'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', quality = qlty, language = lang, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if 'magnet' in item.url:
        itemlist.append(item.clone( url = item.url, server = 'torrent' ))
        return itemlist

    if item.url.endswith('.torrent'):
        itemlist.append(item.clone( url = item.url, server = 'torrent' ))
        return itemlist

    url = item.url

    if PY3:
        from core import requeststools
        data = requeststools.read(url, '')
    else:
        data = do_downloadpage(url)

    if data:
        if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
            return 'Archivo [COLOR red]Inexistente[/COLOR]'

        import os

        file_local = os.path.join(config.get_data_path(), "temp.torrent")
        with open(file_local, 'wb') as f: f.write(data); f.close()

        itemlist.append(item.clone( url = file_local, server = 'torrent' ))

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
