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
import requests
from lib import servop
import os

canonical = {
             'channel': 'ultrahorny', 
             'host': config.get_setting("current_host", 'ultrahorny', default=''), 
             'host_alt': ["https://ultrahorny.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "categories/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&filter=latest" % (host,texto)
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
    matches = soup.find('main', id='main').find_all('a', class_='tag-cloud-link')
    for elem in matches:
        url = elem['href']
        title = elem['aria-label']
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='videos-list').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling('li').a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    if "/?s=" in item.url:
        matches = soup.find('section', id='primary').find_all('article')
    else:
        matches = soup.find('div', class_='videos-list').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        time = elem.find('i', class_='fa-clock-o')
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.parent.text.strip(), title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page and next_page.parent.find_next_sibling("li"):
        next_page = next_page.parent.find_next_sibling('li').a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('div', class_='responsive-player').iframe['src']
    if "/player-x.php?q=" in url:
        import base64
        url = scrapertools.find_single_match(url, "q=([^']+)")
        url = base64.b64decode(url).decode('utf-8')
        url = urlparse.unquote(url)
        url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
    itemlist.append(Item(channel=item.channel, title='%s', contentTitle = item.contentTitle, url=url, action='play'))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('div', class_='responsive-player').iframe['src']
    if "/player-x.php?q=" in url:
        import base64
        url = scrapertools.find_single_match(url, "q=([^']+)")
        url = base64.b64decode(url).decode('utf-8')
        url = urlparse.unquote(url)
        url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
    itemlist.append(Item(channel=item.channel, title='%s', contentTitle = item.contentTitle, url=url, action='play'))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())
    return itemlist

