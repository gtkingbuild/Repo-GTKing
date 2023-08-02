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
             'channel': 'jizzbunker', 
             'host': config.get_setting("current_host", 'jizzbunker', default=''), 
             'host_alt': ["https://jizzbunker.com"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="lista", url=host + "/en/newest"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=host + "/en/straight/popular1"))
    itemlist.append(Item(channel=item.channel, title="Tendencia" , action="lista", url=host + "/en/straight/trending"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/en/channels/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/en/search?query=%s/" % (host, texto)
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
    patron  = '<li><figure>.*?<a href="([^"]+)".*?'
    patron += '<img class="lazy" data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="score">(\d+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for url,thumbnail,title,cantidad in matches:
        plot = ""
        url = url.replace("channel", "channel30")
        title = "%s (%s)" %(title,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail , thumbnail=thumbnail, plot=plot))
    itemlist.sort(key=lambda x: x.title)
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<li><figure>.*?<a href="([^"]+)".*?'
    patron += '<img class="lazy" data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<time datetime=".*?">([^"]+)</time>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,thumbnail,title,duracion in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" %(duracion,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail , thumbnail=thumbnail, plot=plot))
    next_page = scrapertools.find_single_match(data,'<li><a href="([^"]+)" rel="next">&rarr;</a>')
    if next_page !="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = 'type:\'video/mp4\',src:\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl  in matches:
        scrapedurl = scrapedurl.replace("https", "http")
        itemlist.append(Item(channel=item.channel, action="play", title="Directo", url=scrapedurl))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = 'type:\'video/mp4\',src:\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl  in matches:
        scrapedurl = scrapedurl.replace("https", "http")
        itemlist.append(Item(channel=item.channel, action="play", contentTitle=item.title, url=scrapedurl))
    return itemlist