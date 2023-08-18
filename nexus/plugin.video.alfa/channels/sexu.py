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
from core import jsontools as json


canonical = {
             'channel': 'sexu', 
             'host': config.get_setting("current_host", 'sexu', default=''), 
             'host_alt': ["https://sexu.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "new"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "engaging"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "all"))
    itemlist.append(Item(channel=item.channel, title="Mas comentados" , action="lista", url=host + "trending")) 
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories?sort=name"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?q=%s&st=upload" % (host, texto)
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<a class="item" href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += '<div class="item__counter">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        if not scrapedthumbnail.startswith("https"):
            thumbnail = "http:%s" % scrapedthumbnail
        url = urlparse.urljoin(host,scrapedurl)
        url +="?st=upload"
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<a class="pagination__arrow pagination__arrow--next" href="([^"]+)">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<a class="item__main" href="/([^"]+)/" title="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += '<div class="item__counter">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,time in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        if not scrapedthumbnail.startswith("https"):
            thumbnail = "http:%s" % scrapedthumbnail
        url = 'videoId=%s' %scrapedurl
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<a class="pagination__arrow pagination__arrow--next" href="([^"]+)">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = '%sapi/video-info' %host
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = httptools.downloadpage(url, post=item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    JSONData = json.load(data)
    for cat in  JSONData["sources"]:
        url = cat["src"]
        quality = cat["quality"]
        if not url.startswith("https"):
            url = "https:%s" % url
        itemlist.append(Item(channel=item.channel, action="play", title=quality, url=url) )
    return itemlist[::-1]


def play(item):
    logger.info()
    itemlist = []
    url = '%sapi/video-info' %host
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = httptools.downloadpage(url, post=item.url, headers=headers, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    JSONData = json.load(data)
    for cat in  JSONData["sources"]:
        url = cat["src"]
        quality = cat["quality"]
        if not url.startswith("https"):
            url = "https:%s" % url
        itemlist.append(['[sexu] %s' %quality, url])
    return itemlist[::-1]