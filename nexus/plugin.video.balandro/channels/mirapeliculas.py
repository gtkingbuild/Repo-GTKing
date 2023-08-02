# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://mirapeliculasde.com/'

perpage = 20


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'repelis/estrenos/ '))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Categorías<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)" title="(.*?)"')

    for url, title in matches:
        if '/proximos-estrenos/' in url: continue

        title = title.replace('ver películas de', '').strip()

        itemlist.append(item.clone( action='list_all', title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'repelis/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'repelis/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'repelis/subtituladas/' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    patron  = '<div class="col-mt-5 postsh">.*?<a href="([^"]+)".*?'
    patron += '<span class="under-title-gnro">([^"]+)</span>.*?'
    patron += '<p>(\d+)</p>.*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'title="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, qlty, year, thumb, title in matches[item.page * perpage:]:
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

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
            if '<div class="pagenavi">' in data:
                next_page = scrapertools.find_single_match(data,'<span class="current">\d+</span>.*?<a href="([^"]+)"')

                if next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    patron = 'Reproducir</a></td>\n.*?<td>([^<]+)</td>\n.*?<td>([^<]+)</td>\n.*?<td><img src="([^"]+)"'

    matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    for lang, qlty, url in matches:
        ses += 1

        url = url.replace('https://www.google.com/s2/favicons?domain=', '')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if '/hqq.' in url or '/waaw.' in url or '/netu' in url: continue

        if servidor:
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'buscar/?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
