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
             'channel': 'mangovideo', 
             'host': config.get_setting("current_host", 'mangovideo', default=''), 
             'host_alt': ["https://mangovideo.pw/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

#  LINKS CAIDOS server 17 sin definir y pasar a KTP

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "latest-updates/?sort_by=post_date&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "most-popular/?sort_by=video_viewed_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "top-rated/?sort_by=rating_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Sitios" , action="categorias", url=host + "sites/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/"))
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<a class="item" href="([^"]+)" title="([^"]+)".*?'
    patron += '<div class="videos">(\d+) videos</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        title = "%s (%s)"  %(scrapedtitle,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    itemlist.sort(key=lambda x: x.title)
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="item\s+">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<div class="duration">([^<]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedtime in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" % (scrapedtime,scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="next">.*?data-parameters="([^"]+)"')
    if next_page:
        next_page = next_page.replace(":", "=").replace(";", "&").replace("+from_albums", "")
        next_page = "?%s" % next_page
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    url = ""
    url = scrapertools.find_single_match(data, 'src="(https://mangovideo.pw/embed/\d+)"')
    if not url:
        url = scrapertools.find_single_match(data, '<div class="embed-wrap".*?<iframe src="([^"]+)\?ref=')
    itemlist.append(Item(channel=item.channel, action="play", title="%s", url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    url = ""
    url = scrapertools.find_single_match(data, 'src="(https://mangovideo.pw/embed/\d+)"')
    if not url:
        url = scrapertools.find_single_match(data, '<div class="embed-wrap".*?<iframe src="([^"]+)\?ref=')
    itemlist.append(Item(channel=item.channel, action="play", title="%s", url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist