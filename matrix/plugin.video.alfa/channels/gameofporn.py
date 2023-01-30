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

# gameofporn  veporns  https://www.veporno.net  https://www.fxporn.net      http://www.veporns.com    
canonical = {
             'channel': 'gameofporn', 
             'host': config.get_setting("current_host", 'gameofporn', default=''), 
             'host_alt': ["https://www.veporno.net/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*type="?application/rss+xml"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/1"))
    itemlist.append(Item(channel=item.channel, title="Top" , action="lista", url=host + "top-videos"))
    itemlist.append(Item(channel=item.channel, title="New PornStar" , action="catalogo", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Top PornStar" , action="catalogo", url=host + "pornstars?sort=rank"))
    itemlist.append(Item(channel=item.channel, title="Sitios" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%sporn/%s" % (host, texto)
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
    soup = create_soup(item.url).find('div', class_='box')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.a['style']
        thumbnail = scrapertools.find_single_match(thumbnail, 'url\(([^\)]+)')
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail ))
    next_page = soup.find('p', class_='sayfalama').find('a', class_='active')
    if next_page:
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='content')
    matches = soup.find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.text
        url = urlparse.urljoin(host,url)
        thumbnail = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail ))
    return sorted(itemlist, key=lambda i: i.title)


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
    if "/star/" in item.url:
        matches = soup.find('div', class_='videos').find_all('li')
    else:
        matches = soup.find('div', class_='box').find_all('li', class_='dvd-new')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.find('img'):
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.a['style']
            thumbnail = scrapertools.find_single_match(thumbnail, 'url\(([^\)]+)')
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, contentTitle=title,
                             fanart=thumbnail, thumbnail=thumbnail ))
    next_page = soup.find('p', class_='sayfalama').find('a', class_='active')
    if next_page:
        next_page = next_page.find_next_sibling("a")
        if next_page:
            next_page = next_page['href']
            next_page = urlparse.urljoin(item.url,next_page)
            itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='player')
    url = soup.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='player')
    url = soup.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
