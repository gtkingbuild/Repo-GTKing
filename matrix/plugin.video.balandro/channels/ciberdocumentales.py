# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.ciberdocumentales.com'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data
    bloque = scrapertools.find_single_match(data, '<div id="menu">(.*?)</div>')

    patron = ' href="(/[^"]+)">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title.capitalize(), url= host + url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="fotonoticia">\s*<a\s*target="_blank" href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    patron += ' /></a><br /><br />\s*</div>\s*<div class="textonoticia">.*?<br /><br />(.*?)</div>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, plot in matches:
        title = title.capitalize()
        url = host + url

        thumb = host + thumb
        plot = scrapertools.htmlclean(plot)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, plot = plot,
                                    contentType='movie', infoLabels={"year": '-', "plot": plot}, contentTitle=title, contentExtra='documentary' ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page_link = scrapertools.find_single_match(data, '<span class="current">\d*</span>&nbsp;<a href="([^"]+)')
        if next_page_link != '':
            itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = host + next_page_link, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<param name="movie" value="([^"]+)')
    if url:
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url = url, language = 'Esp' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/index.php?categoria=0&keysrc=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
