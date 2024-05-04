# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import scrapertools
from core.item import Item
from platformcode import logger, config
from core import httptools

canonical = {
             'channel': 'ecarteleratrailers', 
             'host': config.get_setting("current_host", 'ecarteleratrailers', default=''), 
             'host_alt': ["https://www.ecartelera.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    if item.url == "":
        item.url = host + 'videos/'

    # ------------------------------------------------------
    # Descarga la página
    # ------------------------------------------------------
    data = httptools.downloadpage(item.url, canonical=canonical).data

    # ------------------------------------------------------
    # Extrae las películas
    # ------------------------------------------------------
    patron = '<div class="viditem"[^<]+'
    patron += '<div class="fimg"><a href="([^"]+)"><img alt="([^"]+)"\s*src="([^"]+)"\s*/><p class="length">([^<]+)</p></a></div[^<]+'
    patron += '<div class="fcnt"[^<]+'
    patron += '<h4><a[^<]+</a></h4[^<]+'
    patron += '<p class="desc">([^<]+)</p>'
    
    #logger.info(patron)
    #logger.info(data)

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, duration, scrapedplot in matches:
        title = scrapertools.htmlclean(scrapedtitle + " (" + duration + ")")
        url = scrapedurl
        thumbnail = scrapedthumbnail
        #mejora imagen
        thumbnail = re.sub('/(\d+)_th.jpg', '/f\\1.jpg', thumbnail)
        plot = scrapedplot.strip()

        logger.debug("title=[" + title + "], url=[" + url + "], thumbnail=[" + thumbnail + "]")
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail,
                 plot=plot,folder=False))

    # ------------------------------------------------------
    # Extrae la página siguiente
    # ------------------------------------------------------
    patron = '<a href="([^"]+)">Siguiente</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = "Pagina siguiente"
        scrapedurl = match
        scrapedthumbnail = ""
        scrapeddescription = ""

        # Añade al listado de XBMC
        itemlist.append(Item(channel=item.channel, action="mainlist", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, server="directo", folder=True,
                             viewmode="movie_with_plot"))

    return itemlist


# Reproducir un vídeo
def play(item):
    logger.info()
    itemlist = []
    # Descarga la página
    data = httptools.downloadpage(item.url).data
    logger.info(data)

    # Extrae las películas
    patron = '<source src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        url = urlparse.urljoin(item.url, matches[0])
        logger.info("url=" + url)
        itemlist.append(Item(channel=item.channel, action="play", title=item.title, url=url, thumbnail=item.thumbnail,
                             plot=item.plot, server="directo", folder=False))

    return itemlist
