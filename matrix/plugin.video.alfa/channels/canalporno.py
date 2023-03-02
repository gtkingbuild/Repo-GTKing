# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from platformcode import config, logger

canonical = {
             'channel': 'canalporno', 
             'host': config.get_setting("current_host", 'canalporno', default=''), 
             'host_alt': ["https://www.canalporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, action="lista", title="Útimos videos", url=host + "ajax/homepage/?page=1"))
    itemlist.append(Item(channel = item.channel, action="categorias", title="Canal", url=host + "ajax/list_producers/?page=1"))
    itemlist.append(Item(channel = item.channel, action="categorias", title="PornStar", url=host + "ajax/list_pornstars/?page=1"))
    itemlist.append(Item(channel = item.channel, action="categorias", title="Categorias", url=host + "categorias"))
    itemlist.append(Item(channel = item.channel, action="search", title="Buscar"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sajax/new_search/?q=%s&page=1" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    if "pornstars" in item.url:
        patron = '<div class="muestra.*?href="([^"]+)".*?src=\'([^\']+)\'.*?alt="([^"]+)".*?'
    else:
        patron = '<div class="muestra.*?href="([^"]+)".*?src="([^"]+)".*?alt="([^"]+)".*?'
    if "Categorias" in item.title:
        patron += '<div class="numero">([^<]+)</div>'
    else:
        patron += '</span> (\d+) vídeos</div>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, scrapedthumbnail, scrapedtitle, cantidad in matches:
        cantidad = cantidad.replace("(", "").replace(")", "")
        title= "%s (%s)" % (scrapedtitle, cantidad) 
        url= url.replace("/videos-porno/", "/ajax/show_category/").replace("/sitio/", "/ajax/show_producer/").replace("/pornstar/", "/ajax/show_pornstar/")
        url = urlparse.urljoin(item.url,url)
        url += "?page=1"
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                             fanart=scrapedthumbnail, thumbnail=scrapedthumbnail))
    if "/?page=" in item.url:
        next_page=item.url
        num= int(scrapertools.find_single_match(item.url,".*?/?page=(\d+)"))
        num += 1
        next_page = "?page=%s" % str(num)
        if next_page!="":
            next_page = urlparse.urljoin(item.url,next_page)
            itemlist.append(Item(channel = item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '<div class="muestra-canal">.*?'
    patron += 'href="([^"]+)".*?'
    patron += 'data-stats-video-name="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += '</span> ([^"]+) min</div>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail, duration in matches:
        title = "[COLOR yellow] %s  [/COLOR] %s" % (duration, scrapedtitle)
        url = urlparse.urljoin(item.url,scrapedurl)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, contentTitle=title,
                                   fanart=scrapedthumbnail, thumbnail=scrapedthumbnail))
    last=scrapertools.find_single_match(item.url,'(.*?)page=\d+')
    num= int(scrapertools.find_single_match(item.url,".*?/?page=(\d+)"))
    num += 1
    next_page = "page=%s" % str(num)
    if next_page!="":
        next_page = last + next_page
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.contentTitle, url=item.url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist
