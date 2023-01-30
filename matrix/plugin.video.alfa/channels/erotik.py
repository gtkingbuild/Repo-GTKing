# -*- coding: utf-8 -*-
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
from bs4 import BeautifulSoup

canonical = {
             'channel': 'erotik', 
             'host': config.get_setting("current_host", 'erotik', default=''), 
             'host_alt': ["https://www.vipporns.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="lista", title="Útimos videos", url= host + "latest-updates/?sort_by=post_date&from=1"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Populares", url=host + "most-popular/?sort_by=video_viewed_month&from=1"))
    itemlist.append(Item(channel=item.channel, action="lista", title="Mejor valorado", url=host + "top-rated/?sort_by=rating_month&from=1"))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Canal", url=host + "categories/"))

    itemlist.append(Item(channel=item.channel, action="search", title="Buscar"))
    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearches/%s/?sort_by=post_date" % (host,texto)
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
    data = re.sub(r"\n|\r|\t|\s{2}", "", data)
    patron = '<a class="item" href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="videos">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,cantidad in matches:
        title= "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail =scrapedthumbnail
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                             thumbnail=thumbnail, fanart=thumbnail))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|\s{2}", "", data) #quita espacio doble
    patron = '<div class="item">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<div class="duration">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    itemlist = []
    for scrapedurl,scrapedtitle,scrapedthumbnail,time in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        thumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail, plot=plot)) # viewmode="movie", folder=True
    next_page = scrapertools.find_single_match(data, 'data-parameters="([^"]+)">Next')
    if next_page:
        next_page = next_page.replace(":", "=").replace(";", "&").replace("+from_albums", "")
        next_page = "?%s" % next_page
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find(string=re.compile("Models:"))
    pornstars = matches.parent.find_all('a')
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    lista = item.contentTitle.split()
    lista.insert (2, pornstar)
    item.contentTitle = ' '.join(lista)    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
