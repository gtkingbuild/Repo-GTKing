# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channelselector import get_thumb
from modules import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger


IDIOMAS = {'Latino': 'Latino'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fembed', 'streamtape', 'fastplay', 'gvideo', 'netutv', 'Jawcloud']

canonical = {
             'channel': 'cinelibreonline', 
             'host': config.get_setting("current_host", 'cinelibreonline', default=''), 
             'host_alt': ["https://www.cinelibreonline.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
__channel__ = canonical['channel']
encoding = None

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True

max_result = 14

def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", url = host + "search?max-results=%s" %max_result, thumbnail = get_thumb("newest", auto = True)))
    itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos", url = host, extra = "Genero", thumbnail = get_thumb("genres", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host, thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist

def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding="utf-8", canonical=canonical).data
    data = data.replace("&nbsp;","")
    patron  = "(?is)post-title entry.*?href='([^']+)'>"
    patron += "([^<]+)"
    patron += '.*?tulo original</i>: <b>([^<]+)'
    patron += ".*?<i>.*?Año</i>: ([^<]+)"
    patron += '.*?<a href="([^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedcontentTitle, scrapedyear, scrapedthumbnail in matches:
        idioma = "Latino"
        item.infoLabels['year'] = scrapedyear
        itemlist.append(item.clone(channel = item.channel,
                                   action = "findvideos",
                                   title = scrapedtitle,
                                   contentTitle = scrapedcontentTitle,
                                   thumbnail = scrapedthumbnail,
                                   url = scrapedurl,
                                   contentType="movie",
                                   language = idioma
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    url_pagina = scrapertools.find_single_match(data, """blog-pager-older-link.*?href='([^']+)""")
    if url_pagina:
        mr = scrapertools.find_single_match(url_pagina, "&max-results=\w+")
        if not url_pagina.endswith("&"): url_pagina += "&"
        url_pagina = url_pagina.replace(mr,"") + "max-results=%s" %max_result
        pagina = "Pagina siguiente"
        itemlist.append(Item(channel = item.channel, action = "peliculas", title = pagina, url = url_pagina))
    return itemlist


def findvideos(item):
    itemlist = []
    
    data = httptools.downloadpage(item.url, encoding="utf-8", canonical=canonical).data.replace("í","i")
    patron  = '(?is)>ver \w+ online:.*?href="([^"]+)'
    patron += '.*?/span>.*?\(([^\)]+)'
    matches = scrapertools.find_multiple_matches(data, patron )
    for scrapedurl, scrapedlang in matches:
        itemlist.append(item.clone(
                        language="Latino",
                        title='[%s] ' + scrapedlang, action="play",
                        url=scrapedurl
                       ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(Item(channel=item.channel))
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))

        # Opción "Añadir esta película a la videoteca de KODI"
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas']:
            item.url = host + "search?max-results=%s" %max_result
        itemlist = peliculas(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "search?q=" + texto
    item.extra = "busca"
    try:
        if texto != '':
            return peliculas(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding="utf-8", canonical=canonical).data
    patron = """(?is)data-version='1' id='HTML6'>.*?widget-content(.*?)widget-content"""
    bloque = scrapertools.find_single_match(data, patron)
    patron   = '(?is)href="([^"]+)'
    patron  += '.*?src="([^"]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedthumbnail in matches:
        scrapedtitle = scrapedurl.replace("-"," ").replace(" online","")
        scrapedtitle = scrapertools.find_single_match(scrapedtitle, '/p/(.*).h')
        itemlist.append(Item(channel = item.channel,
                             action = "list_all",
                             thumbnail = scrapedthumbnail,
                             title = scrapedtitle.capitalize(),
                             url = scrapedurl
                             ))
    return itemlist
    

def list_all(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, encoding="utf-8", canonical=canonical).data
    patron = """(?is)id='post-body(.*?)clear: both;"""
    bloque = scrapertools.find_single_match(data, patron)
    patron   = 'href="([^"]+)'
    patron  += '.*?alt="([^"]+)'
    patron  += '.*?src="([^"]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    item.infoLabels['year'] = "-"
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        itemlist.append(Item(channel = item.channel,
                             action = "findvideos",
                             contentTitle = scrapedtitle,
                             thumbnail = scrapedthumbnail,
                             infoLabels = item.infoLabels,  
                             title = scrapedtitle,
                             url = scrapedurl
                             ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    return itemlist
    

def play(item):
    item.thumbnail = item.contentThumbnail
    if "wikipedia" in item.url:
        data = httptools.downloadpage(item.url, encoding="utf-8").data
        item.url = "https:" + scrapertools.find_single_match(data, '<source src="([^"]+)')
    return [item]
