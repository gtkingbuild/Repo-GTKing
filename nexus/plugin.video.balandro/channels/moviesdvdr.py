# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.moviesdvdr.co/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En DVDrip', action = 'list_all', url = host + 'genero/dvdrip/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<nav class="menu">(.*?)</nav>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if '/dvdrip/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url, text_color = 'deepskyblue' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</h2>(.*?)</main>')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="item hitem">(.*?)</a></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="titulo">.*?<span>(.*?)</span>')

        if not url or not title: continue

        title = title.replace('&#8217;s', "'s").replace('&#8217;', '')

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if "<div class='wp-pagenavi'" in data:
           next_url = scrapertools.find_single_match(data, "<div class='wp-pagenavi'.*?class='current'>.*?" + 'href="(.*?)"')

           if next_url:
               if '/page/' in next_url:
                   itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Version subtitulada': 'Vose'}

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<a class="torrent_download linkastro".*?href="(.*?)"')

    for url in links:
        if url.startswith("//"): url = 'https:' + url
        elif url.startswith("/"): url = host[:-1] + url

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = 'Esp' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        data = do_downloadpage(item.url)

        if data:
            if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
               return 'Archivo [COLOR red]Inexistente[/COLOR]'

        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

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
