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
#SERVER BRAVOPORN lento
canonical = {
             'channel': 'perfectgirls', 
             'host': config.get_setting("current_host", 'perfectgirls', default=''), 
             'host_alt': ["https://www.perfectgirls.net/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Top" , action="lista", url=host + "top/3days/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s/" % (host, texto)
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
    patron  = '<li class="additional_list__item"><a href="([^"]+)">([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        url = urlparse.urljoin(item.url,scrapedurl) + "/1"
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                               thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<div class="list__item_link">.*?'
    patron  += 'href="([^"]+)".*?'
    patron  += 'data-original="([^"]+)".*?'
    patron  += '<span>([^<]+)</span><time>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion in matches:
        plot = ""
        time = scrapertools.find_single_match(duracion, '([^"]+)</time>')
        if not 'HD' in duracion :
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,scrapedtitle)
        else:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,scrapedtitle)
        if not scrapedthumbnail.startswith("https"):
            scrapedthumbnail = "https:%s" % scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=scrapedthumbnail,
                              fanart=scrapedthumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<a class="btn_wrapper__btn" href="([^"]+)">Next</a></li>')
    if next_page:
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page ))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<source src="([^"]+)" res="\d+" label="([^"]+)" type="video/mp4"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,quality in matches:
        if not url.startswith("https"):
            url = "http:%s" % url
        itemlist.append(Item(channel=item.channel, action="play", title=quality, url=url) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<source src="([^"]+)" res="\d+" label="([^"]+)" type="video/mp4"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,quality in matches:
        if not url.startswith("https"):
            url = "http:%s" % url
        itemlist.append(['%s' %quality, url])
    return itemlist