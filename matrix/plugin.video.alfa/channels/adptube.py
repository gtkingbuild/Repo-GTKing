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
             'channel': 'adptube', 
             'host': config.get_setting("current_host", 'adptube', default=''), 
             'host_alt': ["https://www.adptube.com/"], 
             'host_black_list': [], 
             'pattern': ['base href="([^"]+)"'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel = item.channel, title="Nuevos" , action="lista", url=host + "videos?order_by=date_publish"))
    itemlist.append(Item(channel = item.channel, title="Mas vistos" , action="lista", url=host + "videos/?order_by=views_count"))
    itemlist.append(Item(channel = item.channel, title="Canal" , action="categorias", url=host + "series"))
    itemlist.append(Item(channel = item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    # itemlist.append(Item(channel = item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/" % (host,texto)
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
    matches = soup.find_all('div', class_='col-md-2')
    if "series" in item.url:
        matches = soup.find_all('div', class_='col-md-3')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.find('div', class_='size-maintained')['style']
        cantidad = elem.find('div', class_='scenes-count')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = thumbnail.replace("background-image: url(", "").replace(");", "")
        plot = ""
        itemlist.append(Item(channel = item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot) )
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
    matches = soup.find_all('div', class_='col-md-3')
    for elem in matches:
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        time = elem.find('div', class_='corner-right-bottom')
        actriz = []
        plot = ""
        if not "/serie/" in url:
            reparto = elem.find('div', class_='performers').find_all('a')
            for elem in reparto:
                if not "Actriz Porno" in elem['title']:
                    actriz.append(elem['title'])
            actriz = ", ".join(actriz)
            if actriz:
                plot = actriz
                actriz = "%s" %actriz
        if time:
            title = "[COLOR yellow]%s[/COLOR] [COLOR cyan]%s[/COLOR] %s" % (time.text.strip(), actriz, title)
        url = urlparse.urljoin(host, url)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        if not "/serie/" in url:
            itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                   plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
