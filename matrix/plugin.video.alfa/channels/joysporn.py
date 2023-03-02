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

# https://joysporn.sex   https://tubxporn.xxx https://www.pornky.com  https://www.pornktube.porn
canonical = {
             'channel': 'joysporn', 
             'host': config.get_setting("current_host", 'joysporn', default=''), 
             'host_alt': ["https://joysporn.sex/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "videos/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "most-popular/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "top-rated/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories.html"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%sindex.php?do=search&subaction=search&story=%s&search_start=1" % (host,texto)
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
    matches = soup.find('div', class_='porncategories').find_all('a')
    for elem in matches:
        url = elem['href']
        thumbnail = elem.img['src']
        title = elem.find('h2').text
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail, plot=plot))
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
    matches = soup.find_all('div', class_='video_c')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('h2').text.strip()
        thumbnail = elem.img['src']
        time = elem.find('div', class_='vidduration').text.strip()
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail, plot=plot))
    pagination = soup.find('div', class_='navigation')
    next_page = ""
    if pagination:
        if pagination.span.find_next_sibling("a"):
            next_page = pagination.span.find_next_sibling("a")['href']
        if "#" in next_page:
            next_page = pagination.span.find_next_sibling("a").text
            next_page = re.sub(r"&search_start=\d+", "&search_start={0}".format(next_page), item.url)
    if next_page:
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

