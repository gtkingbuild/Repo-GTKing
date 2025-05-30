﻿# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://2000peliculassigloxx.com/'


perpage = 25


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...[COLOR plum](excepto en YouTube)[/COLOR]', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'YouTube', action = 'youtubes', thumbnail=config.get_thumb('youtube'), search_type = 'movie', text_color = 'moccasin' ))

    itemlist.append(item.clone ( title = 'Con acento español', action = 'list_films', url = host + 'especial-peliculas-con-acento-espanol/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Sagas', action = 'sagas', url = host + 'sagas/sagas-pag1/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Navidad', action = 'list_films', url = host + 'especial-navidad/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por actor', action = 'listas', url = host + 'actores/actores-pag1/', group = 'Actores' ))
    itemlist.append(item.clone ( title = 'Por actriz', action = 'listas', url = host + 'actrices/actrices-pag1/', group = 'Actrices' ))
    itemlist.append(item.clone ( title = 'Por dirección, guionista, productor', action = 'listas', url = host + 'directores/directores-pag1/', group = 'Directores' ))
    itemlist.append(item.clone ( title = 'Por compositor, escritor, novelista', action = 'listas', url = host + 'otras-biografias/', group = 'Otras biografías' ))

    return itemlist


def youtubes(item):
    logger.info()
    itemlist = []

    text_color = 'moccasin'

    itemlist.append(item.clone ( title = 'Cine Clásico', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=r9y9RcsBv9k&list=PL5Elc2OLiWk6pkscyMTC6DCbE4GIeqfAe&index=2', text_color=text_color ))

    itemlist.append(item.clone ( title = 'Cine Clásico Español', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=OVjZTR0w_n4&list=PLhgZbivoHwSViCGE5ljvi8cYTgouloz_-', text_color=text_color ))

    itemlist.append(item.clone ( title = 'Otras de Cine Clásico', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=_ppHqkSS_uQ&list=PL5Elc2OLiWk6pkscyMTC6DCbE4GIeqfAe', text_color=text_color ))

    itemlist.append(item.clone ( title = 'Bud Spencer & Terence Hill', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=PuMlIOHBaqg&list=PLy-qmp54bpB2yopTCH_4G5WLnniNQerQf', text_color=text_color ))

    itemlist.append(item.clone ( title = 'Cantinflas', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=U5neiehwYMk&list=PLEN1o4MXDPxA-o78qTZRqEU-XgRUyh76u', text_color=text_color ))

    itemlist.append(item.clone ( title = 'Westerns', action = 'list_tubes', url = 'https://www.youtube.com/watch?v=1g_SGZn4_-c&list=PLLxxgrF1QnBjEvwkfWLPkr-CLEeEHJuWl', text_color=text_color ))

    return itemlist


def list_tubes(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(str(data), '"playlist":.*?"playlist":.*?"title":(.*?)$')

    matches = scrapertools.find_multiple_matches(str(bloque), 'playlistPanelVideoRenderer":.*?simpleText":"(.*?)".*?"videoId":"(.*?)".*?"playlistId"')

    for title, _id in matches:
        if not _id or not title: continue

        thumb = 'https://i.ytimg.com/vi/' + _id + '/hqdefault.jpg'

        url = 'https://www.youtube.com/watch?v=' + _id

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, group = 'youtubes' ))

    return itemlist


def sagas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(str(data), '<div class="container-fluid">(.*?)</a></div></div>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?src="(.*?)".*?alt="(.*?)"')

    for url, thumb, title in matches:
        if not title or not url: continue

        itemlist.append(item.clone( action = 'list_films', title = title, url = url, thumbnail = thumb, text_color = 'moccasin' ))

    if itemlist:
        if '<ul class="pagination' in data:
            next_page = scrapertools.find_single_match(data, '<ul class="pagination.*?<li class="page-item active success">.*?</li>.*?href="(.*?)"')

            if next_page:
                if '-pag' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', url = next_page, action = 'sagas', text_color='coral' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '>Décadas<(.*?)>Biografías<')

    matches = scrapertools.find_multiple_matches(bloque, '<li id=".*?<a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        if not url or not title: continue

        if not '/anos-' in url: continue

        itemlist.append(item.clone( action = 'list_films', title = title, url = url, text_color = 'deepskyblue' ))

    return itemlist


def listas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if '/otras-biografias' in item.url:
        bloque = scrapertools.find_single_match(data, '>' + item.group + '<(.*?)</main>')

        matches = scrapertools.find_multiple_matches(bloque, '<li><a href="([^"]+)".*?rel="noopener noreferrer">(.*?)</a>')

        for url, title in matches:
            if not url or not title: continue

            itemlist.append(item.clone( action= 'list_films', title = title, url = url, text_color='tan' ))
    else:
        bloque = scrapertools.find_single_match(str(data), '<div class="container-fluid">(.*?)</a></div></div>')

        matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?src="(.*?)".*?alt="(.*?)"')

        for url, thumb, title in matches:
            if not url or not title: continue

            itemlist.append(item.clone( action = 'list_films', title = title, url = url, thumbnail = thumb, text_color='moccasin' ))

    if itemlist:
        if item.group == 'Directores':
            if '<ul class="pagination' in data:
                next_page = scrapertools.find_single_match(data, '<ul class="pagination.*?<li class="page-item active success">.*?</li>.*?href="(.*?)"')

                if next_page:
                    if '-pag' in next_page:
                        itemlist.append(item.clone( title='Siguientes ...', url = next_page, action = 'listas', text_color='coral' ))

    if not item.group == 'Directores':
       return sorted(itemlist, key = lambda it: it.title)
    else:
       return itemlist


def list_films(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<tr class="row-.*?src="(.*?)".*?alt="(.*?)".*?<a href="(.*?)"')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, title, url in matches[desde:hasta]:
        if not url or not title: continue

        if title == '2000PeliculasSigloXX': continue

        name = title.strip()

        try:
            year = title.split('(')[1]
            year = year.split(',')[0]

            if year:
                title = title.replace(year + ', ', '')

                name = title
                name = name.split('(')[0]
                name = name.strip()
        except:
            year = ''

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            next_page = item.page + 1

            itemlist.append(item.clone( title='Siguientes ...', page = next_page, action = 'list_films', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.group == 'youtubes':
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'youtube', language = 'Esp', url = item.url ))
        return itemlist

    if '.primevideo.' in item.url: return itemlist
    elif '.2000cancionessigloxx.' in item.url: return itemlist

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<source src="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<iframe src="(.*?)"')

    if not url: url = scrapertools.find_single_match(data, '<source type="video/mp4".*?src="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<iframe type="video/mp4".*?src="(.*?)"')

    url = url.replace('https://www.adf.ly/6680622/banner/', '').replace('&amp;', '&')

    if url.startswith('https://ipfs.infura.io/'):
        headers = {'referer': host}
        url = httptools.downloadpage(url, headers = headers, only_headers = True, follow_redirects = False).headers.get('location')

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', language = 'Esp', url = url ))
            return itemlist

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''
        if servidor == 'directo':
            if url.startswith('https://odysee.com'): other = 'Odysee'

        if servidor:
            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Esp', url = url, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'youtube': pass

    elif not url.endswith('.mp4'):
        new_url = httptools.downloadpage(url, follow_redirects=False).headers['location']

        if not new_url: return itemlist

        new_url = new_url.replace('https://streaming.2000peliculassigloxx.com/yandex/yadisk.html?v=', 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key=https://yadi.sk/i/')

        data = httptools.downloadpage(new_url).data

        vid = scrapertools.find_single_match(data, '"href":"(.*?)"')

        if vid: url = vid

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div><a href="(.*?)".*?">(.*?)</a>')

    for url, title in matches:
        if not url or not title: continue

        itemlist.append(item.clone( action = 'list_films', url = url, title = title ))

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
