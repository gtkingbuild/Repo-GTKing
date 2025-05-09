# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://cinekinki.es/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'Servicio.html', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="imagen">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="texto">(.*?)</div>')

        if not url or not title: continue

        if item.filtro:           
            texto_filtro = item.filtro.lower().strip()
            texto_titulo = title.lower()

            if not texto_filtro in texto_titulo: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        thumb = host + thumb

        url = host + url

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = 'Esp',
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<source.*?src="(.*?)"')

    for url in matches:
        url = host + url.replace(" ", "%20")

        age = 'Solo descarga'

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = 'directo', title = '', language = 'Esp', age = age ))

        url = url.replace('.mkv', '.torrent').replace('.mp4', '.torrent')

        if '.torrent' in url:
            itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = 'torrent', title = '', language = 'Esp' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'Servicio.html'
        item.filtro = texto
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

