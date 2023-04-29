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
             'channel': 'xxxdan', 
             'host': config.get_setting("current_host", 'xxxdan', default=''), 
             'host_alt': ["https://xxxdan.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="lista", url=host + "newest"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=host + "straight/popular7"))
    itemlist.append(Item(channel=item.channel, title="HD" , action="lista", url=host + "channel30/hd"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "channels"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?query=%s" % (host, texto)
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
    patron = '<a href="([^"]+)" rel="tag".*?'
    patron += 'title="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<span class="score">(\d+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,cantidad in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" % (scrapedtitle, cantidad)
        scrapedurl = scrapedurl.replace("channel", "channel30")
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail , fanart=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<li><figure>\s*<a href="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<time datetime="\w+">([^"]+)</time>'
    patron += '(.*?)</ul>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,duracion,calidad in matches:
        url = scrapedurl
        scrapedtitle = scrapertools.find_single_match(scrapedurl,'https://xxxdan.com/es/.*?/(.*?).html')
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion, scrapedtitle)
        if '<li class="hd">' in calidad :
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (duracion, scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title , url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data,'<link rel="next" href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    scrapedurl = scrapertools.find_single_match(data, 'src:\'([^\']+)\'')
    scrapedurl = scrapedurl.replace("https","http")
    itemlist.append(Item(channel=item.channel, action="play", title="Directo", url=scrapedurl, contentTitle=item.contentTitle ))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    scrapedurl = scrapertools.find_single_match(data, 'src:\'([^\']+)\'')
    scrapedurl = scrapedurl.replace("https","http")
    itemlist.append(Item(channel=item.channel, action="play", url=scrapedurl, contentTitle=item.contentTitle ))
    return itemlist
