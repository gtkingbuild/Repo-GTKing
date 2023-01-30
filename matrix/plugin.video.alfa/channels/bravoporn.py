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

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

canonical = {
             'channel': 'bravoporn', 
             'host': config.get_setting("current_host", 'bravoporn', default=''), 
             'host_alt': ["https://www.bravoporn.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Nuevas" , action="lista", url=host +"latest-updates/"))
    itemlist.append(Item(channel = item.channel, title="Popular" , action="lista", url=host + "most-popular/"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host + "c/"))
    # itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ss/?q=%s" % (host, texto)
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a href="([^"]+)" class="th">.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<span>([^<]+)</span>\s*(\d+) movies.*?</strong>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" % (scrapedtitle, cantidad)
        scrapedthumbnail = "http:%s" % scrapedthumbnail
        scrapedurl = urlparse.urljoin(item.url,scrapedurl) + "latest/"
        itemlist.append(Item(channel = item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<div class=".*?video_block"><a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?alt="([^"]+)".*?'
    patron += '<span class="time">([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion, scrapedtitle)
        thumbnail = "https:" + scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)" class="[^"]+" title="Next">Next</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info(item)
    itemlist.append(Item(channel = item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info(item)
    itemlist = servertools.find_video_items(Item(channel = item.channel, url = item.url, contentTitle = item.title))
    return itemlist
