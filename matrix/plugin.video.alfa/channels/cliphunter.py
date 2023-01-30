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


host = "https://www.cliphunter.com"


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevas" , action="lista", url=host + "/categories/All"))
    itemlist.append(item.clone(title="Popular" , action="lista", url=host + "/popular/ratings/yesterday"))
    itemlist.append(item.clone(title="Pornstars" , action="catalogo", url=host + "/pornstars/"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/%s" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<a href="([^"]+)">\s*<img src=\'([^\']+)\'/>.*?<span>([^"]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl) + "/movies"
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail , plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li class="arrow"><a rel="next" href="([^"]+)">&raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<a href="([^"]+)" title="([^"]+)">.*?<img src="([^"]+)"/>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<img class=".*?" src="([^"]+)".*?'
    patron += '<div class="tr.*?">([^<]+)</div>.*?'
    patron += '<a href="([^"]+)" class="vttl.*?">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedtime,scrapedurl,scrapedtitle  in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (scrapedtime, scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail, plot=plot,
                              fanart=thumbnail, contentTitle = title ))
    next_page = scrapertools.find_single_match(data,'<li class="arrow"><a rel="next" href="([^"]+)">&raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '"url"\:"(.*?)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl  in matches:
        scrapedurl = scrapedurl.replace("\/", "/")
        title = scrapedurl
    itemlist.append(item.clone(action="play", title="[cliphunter] mp4", url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '"url"\:"(.*?)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl  in matches:
        url = scrapedurl.replace("\/", "/")
        url += "|Referer=%s/" % host
        title = url
    itemlist.append(item.clone(action="play", title="[cliphunter] mp4", url=url))
    return itemlist
