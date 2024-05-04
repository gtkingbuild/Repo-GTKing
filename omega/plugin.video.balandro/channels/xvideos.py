# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.xvideos.com/'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    if config.get_setting('descartar_xxx', default=False): return

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, page = 0 ))

    itemlist.append(item.clone( title = 'Los mejores', action = 'list_best', url = host + 'best/', page = 0 ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels-index', page = 0 ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'list_stars', url = host + 'pornstars-index', page = 0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    external = scrapertools.find_single_match(data, '<a class="external-link" href="(.*?)"')

    matches = re.compile('<div class="thumb"><a href="([^"]+)".*?data-src="([^"]+)".*?title="([^"]+)"').findall(data)

    ses = 0

    for url, thumb, title in matches:
        ses += 1

        if title == 'Modelo verificada':
            title = scrapertools.find_single_match(url, '/video.*?/(.*?)$')
            title = title.replace('_', ' ').strip()
            title = title.capitalize()

        title = title.replace('&aacute;', 'a').replace('&eacute;', 'e').replace('&iacute;', 'e').replace('&oacute;', 'o').replace('&uacute;', 'u')

        title = title.replace('&aacuate;', 'a').replace('&eacuate;', 'e').replace('&iacuate;', 'e').replace('&oacuate;', 'o').replace('&uacuate;', 'u')

        title = title.replace("&#039;", "'").replace('&quot;', '').replace('&iexcl;', '').replace('&ndash;', '').replace('&ntilde;', 'ñ').replace("&rsquo;", "'")

        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a href="([^"]+)" class="no-page next-page">')

        if next_url:
            if not next_url == '#1':
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, action = 'list_all', page = item.page + 1, text_color = 'coral' ))

    if not itemlist:
        if ses == 0:
            if external:
                if not host in external:
                    platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Enlace externo al canal No Admitido[/B][/COLOR]')
                    return

    return itemlist


def list_best(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div id="date-links-pagination" class="ordered-label-list">(.*?)<li class="hidden">')

    matches = re.compile('<li>(.*?)</li>').findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '">(.*?)</a>')

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 250

    data = do_downloadpage(host + 'tags')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="(/tags/[^"]+)"><b>([^<]+)').findall(data)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, title in matches[desde:hasta]:
        titulo = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = titulo, text_color = 'tan' ))

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'categorias', text_color='coral' ))

    return itemlist


def list_stars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="([^"]+)">(.*?)</a>').findall(data)

    for url, title in matches:
        if 'Todas las etiquetas' in title: continue
        elif '&iacuate;' in title: continue

        title = title.replace('&ntilde;', 'ñ')

        itemlist.append(item.clone( action = 'pornstars', url = url if url.startswith('http') else host[:-1] + url, title = title, text_color='moccasin' ))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile(r'xv.thumbs.replaceThumbUrl\(\'<img src="([^"]+)".*?<a href="([^"]+)">([^<]+)').findall(data)

    for thumb, url, title in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb , text_color = 'orange'))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a href="([^"]+)" class="no-page next-page">')

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, action = 'pornstars', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="(\/channels[^"]+)">([^<|\d+]+)').findall(data)

    for url, title in matches:
        title = title.replace('&ntilde;', 'ñ')

        itemlist.append(item.clone( action = 'list_canales', url = url if url.startswith('http') else host[:-1] + url, title = title, text_color = 'orange' ))

    return sorted(itemlist, key=lambda x: x.title)


def list_canales(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="thumb-inside"><div class="thumb"><a href="([^"]+)">.*?xv.thumbs.replaceThumbUrl\(\'<img src="([^"]+)".*?span class="profile-name">([^<]+)'

    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        url = url if url.startswith('http') else host[:-1] + url

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url, action = 'list_canales', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    try:
       m3u8url = re.findall(r"html5player\.setVideoHLS\('([^']+)'", data)[0]
    except:
       return itemlist

    data = do_downloadpage(m3u8url)

    matches = re.compile('(?i)name="([^"]+)"\s*(.*?m3u8)').findall(data)

    for calidad, url in matches:
        if not calidad or not url: continue

        url = m3u8url.replace("hls.m3u8", url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = calidad, url = url, language = 'Vo' ))

    return sorted(itemlist, key=lambda i: i.quality)


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "?k=%s" % (texto.replace(" ", "%20"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
