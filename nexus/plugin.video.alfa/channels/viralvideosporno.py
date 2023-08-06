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
from bs4 import BeautifulSoup
from modules import autoplay

# IDIOMAS = {'vo': 'VO'}
# list_language = list(IDIOMAS.values())
list_quality = ['default']
list_servers = ['aparatcam']

canonical = {
             'channel': 'viralvideosporno', 
             'host': config.get_setting("current_host", 'viralvideosporno', default=''), 
             'host_alt': ["http://www.viralvideosporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    # itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/peliculas/1"))
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "escenas-ultimos-videos/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "escenas-mas-visitados/"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="All" , action="lista", url=host + "peliculas/1"))
    soup = create_soup(item.url)
    matches = soup.find('div', id='movies').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url = urlparse.urljoin(item.url,url)
        thumbnail =  ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sbuscar-%s.html" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find('div', id='categories').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        url = urlparse.urljoin(item.url,url)
        thumbnail =  ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
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


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if "/peliculas/" in item.url:
        matches = soup.find_all('div', class_='portada')
    else:
        matches = soup.find_all('div', class_='notice')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', id=re.compile(r'tab-\d+'))
    for elem in matches:
        video = elem.iframe
        if video:
            url = video['src']
            if "<iframe" in url:
                url = elem.a['src']
            if url:
                itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
        else:
            downlinks = elem.find_all('a', class_='Enlaces')
            for i in downlinks:
                url = i.text
                if not "ddownload" in url:
                    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
