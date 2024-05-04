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
             'channel': 'hellporno', 
             'host': config.get_setting("current_host", 'hellporno', default=''), 
             'host_alt': ["https://hellporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "1/", t=""))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel=item.channel, title="Lesbian" , action="new_menu", url=host, t="lesbian"))
    itemlist.append(Item(channel=item.channel, title="Bisexual" , action="new_menu", url=host, t="bisexual"))
    itemlist.append(Item(channel=item.channel, title="Shemale" , action="new_menu", url=host, t="shemale"))
    itemlist.append(Item(channel=item.channel, title="Gay" , action="new_menu", url=host, t="gay"))

    return itemlist

def new_menu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "1/?t=" + item.t))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/?t="+ item.t))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", t=item.t))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/?q=%s&t=%s" % (host, texto,item.t )
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
    data = scrapertools.find_single_match(data,'<div class="container">(.*?)<div id="aside">')
    patron  = '<a href="([^"]+)">.*?'
    patron += '<img src="([^"]+)" alt="([^"]+) - Porn videos">.*?'
    patron += '<span>(\d+) videos</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" % (scrapedtitle,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail , plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)" class="next">Next page &raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias" , title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<div class="video-thumb"><a href="([^"]+)" class="title".*?>([^"]+)</a>.*?'
    patron += '<span class="time">([^<]+)</span>.*?'
    patron += '<video muted poster="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,duracion,scrapedthumbnail  in matches:
        url = scrapedurl
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion,scrapedtitle)
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)" class="next">Next page &raquo;</a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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