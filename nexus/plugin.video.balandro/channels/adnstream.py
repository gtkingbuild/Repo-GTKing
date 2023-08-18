# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = "https://www.adnstream.com/"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Documentales:', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( title = ' - Destacados', action = 'list_all', url = host + 'canal/Grandes-documentales/', search_type = 'documentary' ))
    itemlist.append(item.clone( title = ' - Viajes', action = 'list_all', url = host + 'canal/Viajes/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Películas:', folder=False, text_color='deepskyblue' ))

    itemlist.append(item.clone( title = ' - Cine de ayer y siempre', action = 'list_all', url = host + 'canal/Cine-de-ayer-y-siempre/', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<span class="videoThumb">.*?href="(.*?)".*?src="(.*?)".*?title="(.*?)"')

    for url, thumb, title in matches:
        if item.search_type == 'documentary':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, contentExtra='documentary' ))
        else:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    if item.search_type == 'movie':
        tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="this pagina">.*?class="pagina">.*?href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "file: '(.*?)'")

    for url in matches:
        itemlist.append(Item( channel = item.channel, action = 'play', server='directo', title = '', url = url, language = 'Esp' ))

    return itemlist


def _ayer_y_siempre(item):
    logger.info()
    itemlist = []

    item.url = host + 'canal/Cine-de-ayer-y-siempre/'
    item.search_type = 'movie'

    return list_all(item)


def search(item, texto):
    logger.info()
    try:
        # ~ No funciona en la Web
        item.url = host + 'search.php?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
