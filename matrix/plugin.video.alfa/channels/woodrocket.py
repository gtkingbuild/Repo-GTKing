# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

canonical = {
             'channel': 'woodrocket', 
             'host': config.get_setting("current_host", 'woodrocket', default=''), 
             'host_alt': ["https://woodrocket.com/"], 
             'host_black_list': [], 
             'pattern': ['<li class="active"><a href="([^"|]+)"'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Novedades" , action="lista", url=host + "porn"))
    itemlist.append(item.clone(title="Parodias" , action="lista", url=host + "parodies"))
    itemlist.append(item.clone(title="Shows" , action="categorias", url=host + "series"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "categories"))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<div class="media-panel-image">.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail =  host + scrapedthumbnail
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<div class="media-panel-image">.*?<a href="([^"]+)".*?title="([^"]+)".*?<img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        plot = ""
        contentTitle = scrapedtitle
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        title = scrapedtitle
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title , url=scrapedurl, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'<li><a href="([^"]+)" rel="next">&raquo;</a></li>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url  = scrapertools.find_single_match(data,'<iframe src="([^"]+)"')
    itemlist.append(item.clone(action="play", title= "%s", url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url  = scrapertools.find_single_match(data,'<iframe src="([^"]+)"')
    itemlist.append(item.clone(action="play", title= "%s", url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist