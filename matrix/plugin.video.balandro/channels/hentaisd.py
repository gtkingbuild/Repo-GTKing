# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools

from lib import jsunpack


host = 'https://hentaisd.tv/'


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'hentai/' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_list', url = host + 'hentai/estrenos/' ))

    itemlist.append(item.clone( title = 'Sin censura', action = 'list_all', url = host + 'hentai/sin-censura/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'hentai/generos/').data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<h3 class="media-heading"><a href="([^"]+)" alt="([^"]+)"', re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_list', url = url, title = title ))

    return sorted(itemlist, key=lambda i: i.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div class="media">.*?<a href="([^"]+)".*?<img src="([^"]+)".*?alt="([^"]+)".*?>([^<]+)</p>', re.DOTALL).findall(data)

    for url, thumb, title, plot in matches:
        title = title.strip()

        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults', infoLabels={'plot': plot} ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def list_list(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div class="col-sm-6 col-md-2 central">.*?<a href="([^"]+)".*?<img src="([^"]+)".*?<h5>([^<]+)</h5>', re.DOTALL).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_list', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<li><a href="([^"]+)".*?Capitulo (\d+)', re.DOTALL).findall(data)

    for url, title in matches:
        title = title + " - " + item.title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title,
                                    contentType = 'movie', contentTitle = title, contentExtra='adults' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>||<br/>', "", data)

    data = scrapertools.find_single_match(data, 'var videos =(.*?)\}')

    matches = re.compile('src="([^"]+)"', re.DOTALL).findall(data)

    for url in matches:
        url = url.replace('cloud/index.php', 'cloud/query.php')

        if "/player.php" in url:
            data = httptools.downloadpage(url).data

            phantom = scrapertools.find_single_match(data, 'Phantom.Start\("(.*?)"\)')
            phantom = phantom.replace('"+"', '')

            packed = base64.b64decode(phantom).decode("utf8")
            unpacked = jsunpack.unpack(packed)

            url = scrapertools.find_single_match(unpacked, '"src","([^"]+)"')

        if url:
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if not servidor == 'directo':
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'VO' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '/buscar/?t=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
