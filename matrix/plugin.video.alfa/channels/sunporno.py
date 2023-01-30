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
             'channel': 'sunporno', 
             'host': config.get_setting("current_host", 'sunporno', default=''), 
             'host_alt': ["https://www.sunporno.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="lista", url=host +"most-recent/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="Popular" , action="lista", url=host + "most-viewed/date-last-month/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "top-rated/date-last-month/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="Mas favoritas" , action="lista", url=host + "mostfavorites/date-last-month/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largas" , action="lista", url=host + "long-movies/date-last-month/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="PornStars" , action="categorias", url=host + "pornstars/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "channels/name/?pageId=1"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s/most-recent/?pageId=1" % (host, texto)
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
    matches = soup.find_all('a', class_='pp')
    for elem in matches:
        # if "Category:" in elem.parent.text: 
        if not elem.find('img'):
            continue
        url = elem['href']
        if not "/channels/" in url:
            title = elem.find('span', class_='video-title').text.strip()
        else:
            title = elem.img['alt']
        if elem.img.get("src", ""):
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.img['data-src']
        cantidad = elem.find('p', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())

        if not "/pornstars/" in url:
            url += "most-recent/?pageId=1"
        else:
            url += "?pageId=1"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot) )
    if not "/channels/" in item.url:
        pagin = soup.find('div', id='pagingAuto')
        page = int(pagin['data-page'])
        page_limit = int(pagin['data-limit'])
        if page <= page_limit:
            next_page = page +1
            next_page = re.sub(r"pageId=\d+", "pageId={0}".format(next_page), item.url)
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
    if "/pornstars/" in item.url:
        matches = soup.find_all('div', class_='th')
    else:
        matches = soup.find_all('div', class_=re.compile(r"^movie-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.find('span', class_='video-title').text.strip()
        if elem.img.get("src", ""):
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.img['data-src']
        if "/pornstars/" in item.url:
            time = elem.find('span', class_='dur').text.strip()
        else:
            time = elem.find('span', class_='btime').text.strip()
        quality = elem.find('i', class_='icon-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    pagin = soup.find('div', id='pagingAuto')
    page = int(pagin['data-page'])
    page_limit = int(pagin['data-limit'])
    if page <= page_limit:
        next_page = page +1
        next_page = re.sub(r"pageId=\d+", "pageId={0}".format(next_page), item.url)
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
