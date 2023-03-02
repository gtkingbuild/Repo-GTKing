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
from channels import autoplay

list_quality = []
list_servers = ['gounlimited']


canonical = {
             'channel': 'pornohdmega', 
             'host': config.get_setting("current_host", 'pornohdmega', default=''), 
             'host_alt': ["https://www.pornohdmega.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host, texto)
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
    patron = '<a href="([^"]+)" class="tag.*?'
    patron += 'aria-label="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        numero = scrapertools.find_single_match(scrapedtitle, '\((\d+)')
        thumbnail = ""
        scrapedplot = ""
        if int(numero) > 10:
            itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                                  thumbnail=thumbnail , plot=scrapedplot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-lazy-src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedplot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                             fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data, '<li><a class="current">.*?<a href="([^"]+)" class="inactive">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        if "0p" in scrapedtitle:
            quality = scrapertools.find_single_match(scrapedtitle, '(\d+p)')
            title = scrapertools.find_single_match(scrapedtitle, '([^"]+)(?:-| |)\d+p')
            title = "[COLOR red]%s[/COLOR] %s" % (quality,title)
        else:
            title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle = title, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot,))
    next_page = scrapertools.find_single_match(data, '<li><a class="current">.*?<a href="([^"]+)" class="inactive">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    video_url = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = scrapertools.find_single_match(data, '<div\s+class="responsive-player"(.*?)<div class="sharing-buttons">')
    patron = '(?:src|SRC)="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        if  not "about:blank" in url and not url in video_url:
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle=item.title, url=url))
        video_url.append(url)
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist


