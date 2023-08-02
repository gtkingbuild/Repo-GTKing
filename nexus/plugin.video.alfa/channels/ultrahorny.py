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
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    # itemlist.append(Item(channel=item.channel, title="Mas visto" , action="lista", url=host + "?filter=most-viewed"))
    # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?filter=popular"))
    # itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "categories/"))
    # itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "tags/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='ctgr')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='ttl').text.strip()
        cantidad = elem.find('span', class_='fwb').text.strip()
        if cantidad:
            title = "%s (%s)" %(title,cantidad)
        thumbnail = ""
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
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
    matches = soup.find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.h2.text.strip()
        thumbnail = elem.img['src']
        time = elem.find('i', class_='fa-clock-o')
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.parent.text.strip(), title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', id='player-torotube')
    if soup.find('source'):
        url = item.url
    else:
        url = soup.iframe['src']
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
    soup = create_soup(item.url).find('div', id='player-torotube')
    if soup.find('source'):
        url = item.url
    else:
        url = soup.iframe['src']
        if "/player-x.php?q=" in url:
            import base64
            url = scrapertools.find_single_match(url, "q=([^']+)")
            url = base64.b64decode(url).decode('utf-8')
            url = urlparse.unquote(url)
            url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
    itemlist.append(Item(channel=item.channel, title='%s', contentTitle = item.contentTitle, url=url, action='play'))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())
    return itemlist

