# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from channelselector import get_thumb
from platformcode import logger, config

canonical = {
             'channel': 'documentalesonline', 
             'host': config.get_setting("current_host", 'documentalesonline', default=''), 
             'host_alt': ["https://www.documentales-online.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = list()
    itemlist.append(Item(channel=item.channel, title="Novedades", action="videos", url=host, page=1,
                         thumbnail=get_thumb('newest', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Destacados", action="seccion", url=host, extra="destacados",
                         thumbnail=get_thumb('hot', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Series destacadas", action="seccion", url=host, extra="series",
                         thumbnail=get_thumb('tvshows', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Categorías", action="categorias", url=host,
                         thumbnail=get_thumb('categories', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Top 100", action="listado", url=host + "top/",
                         thumbnail=get_thumb('more voted', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Populares", action="listado", url=host + "populares/",
                         thumbnail=get_thumb('more watched', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Series / Temas", action="listado", url=host + "series-temas/",
                         thumbnail=get_thumb('tvshows', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search",
                         thumbnail=get_thumb('search', auto=True)))
    return itemlist


def listado(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    bloque = scrapertools.find_single_match(data, 'Populares</a>.*?%s(.*?)</article>' %item.title)
    if "series-temas" not in item.url:
        patron  = '<a href="([^"]+)".*?'
        patron += '>([^"]+)"'
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for scrapedurl, scrapedtitle in matches:
            scrapedtitle = scrapedtitle.split("<")[0]
            itemlist.append(Item(action = "findvideos",
                                 channel = item.channel,
                                 title = scrapedtitle,
                                 url = scrapedurl
                                 ))
    else:
        patron  = """<a href="([^"]+)".*?"""
        patron += """>([^<]+)<.*?"""
        matches = scrapertools.find_multiple_matches(bloque, patron)
        for scrapedurl, scrapedtitle in matches:
            itemlist.append(Item(action = "videos",
                                 channel = item.channel,
                                 title = scrapedtitle,
                                 url = host + scrapedurl
                                 ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    if item.extra == "destacados":
        patron_seccion = 'Destacados(.*?)</ul>'
        action = "findvideos"
    else:
        patron_seccion = 'Series destacadas(.*?)</ul>'
        action = "videos"
    data = scrapertools.find_single_match(data, patron_seccion)
    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)">(.*?)</a>')
    aux_action = action
    for url, title in matches:
        if item.extra != "destacados" and "Cosmos (Carl Sagan)" in title:
            action = "findvideos"
        else:
            action = aux_action
        itemlist.append(item.clone(title=title, url=url, action=action, contentTitle=title))
    return itemlist


def videos(item):
    logger.info()
    itemlist = []
    if item.page:
        data = httptools.downloadpage(item.url + "page/%s" %item.page, canonical=canonical).data
    else:
        data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '(?is)headline"><a href="([^"]+).*?'
    patron += 'bookmark">([^<]+).*?'
    patron += 'src="([^"]+).*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, title, thumb in matches:
        title = title.replace("&#8211;","-")
        title = title.replace("&#8230;","...")
        itemlist.append(item.clone(title=title, url=url, action="findvideos", contentTitle=title, thumbnail=thumb))
    if item.page:
        itemlist.append(item.clone(title=">> Página siguiente", url=host, page=item.page + 1))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = scrapertools.find_single_match(data, 'a href="#">Categor(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)">(.*?)</a>')
    for url, title in matches:
        itemlist.append(item.clone(title=title, url=url, action="videos", contentTitle=title))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    try:
        item.url = host + "?s=%s" % texto
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    if "Cosmos (Carl Sagan)" in item.title:
        patron  = '(?s)<p><strong>([^<]+)<.*?'
        patron += '<iframe.*?src="([^"]+)"'
        matches = scrapertools.find_multiple_matches(data,patron)
        for title, url in matches:
            itemlist.append(item.clone(action = "play", title=title, url=url
                           ))
    else:
        data1 = scrapertools.find_multiple_matches(data, '<iframe.+?src="([^"]+)"')
        itemlist.extend(servertools.find_video_items(data=",".join(data1)))
        for videoitem in itemlist:
            videoitem.contentTitle = item.contentTitle
            videoitem.channel = item.channel
    if not itemlist:
        url = scrapertools.find_single_match(data, '<p>(http://[^<]+)<')
        itemlist.append(item.clone(action = "play", url=url))
    itemlist = servertools.get_servers_itemlist(itemlist)
    return itemlist
