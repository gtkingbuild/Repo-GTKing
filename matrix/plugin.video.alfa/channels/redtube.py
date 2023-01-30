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

from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger

canonical = {
             'channel': 'redtube', 
             'host': config.get_setting("current_host", 'redtube', default=''), 
             'host_alt': ["https://es.redtube.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

#  FALLA 1080

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="lista", url=host + "newest"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="lista", url=host + "mostviewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "top"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channel/top-rated"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="categorias", url=host + "pornstar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/popular"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?search=%s" % (host, texto)
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
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<span class="channel-logo">.*?'
    patron += 'data-src="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '<a href="([^"]+)">.*?'
    patron += 'videos">\s+([^<]+) Videos'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedtitle,scrapedurl,cantidad in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" %(scrapedtitle, cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page_url = scrapertools.find_single_match(data,'<a id="wp_navNext".*?href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page_url) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if "categories" in item.url:
        patron = '<li id="categories_list_block_.*?'
    else:
        patron  = '<li id="recommended_pornstars_block_ps_.*?'
    patron += 'href="([^"]+)".*?'
    patron += 'data-src\s*=\s*"([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += 'count">\s*([^<]+)\s*Videos'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        cantidad = cantidad.strip()
        scrapedtitle = "%s (%s)" %(scrapedtitle, cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page_url = scrapertools.find_single_match(data,'<a id="wp_navNext".*?href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page_url) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = scrapertools.find_single_match(data,'<em class="premium_tab_icon rt_icon rt_Menu_Star">(.*?)<div class="footer">')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<div class="video_block_wrapper js_mediaBookBounds ">.*?'
    patron += 'data-o_thumb="([^"]+)"(.*?)'
    patron += '<span class="duration">(.*?)</a>.*?'
    patron += '<a title="([^"]+)".*?href="(/\d+)"(.*?)</ul'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedhd,duration,scrapedtitle,scrapedurl,pornstars in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        duration = scrapertools.find_single_match(duration, '(\d+:\d+)')
        if "hd-video" in scrapedhd:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (duration,scrapedtitle)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration, scrapedtitle)
        if 'href="/pornstar/' in pornstars:
            pornstars = scrapertools.find_multiple_matches(pornstars, 'href="/pornstar/.*?title="([^"]+)"')
            pornstar = ' & '.join(pornstars)
            pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
            lista = title.split()
            if "HD" in title:
                lista.insert (4, pornstar)
            else:
                lista.insert (2, pornstar)
            title = ' '.join(lista)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title , url=url,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=plot, contentTitle = title) )
    next_page_url = scrapertools.find_single_match(data,'<a id="wp_navNext".*?href="([^"]+)">').replace("amp;", "")
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page_url) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist