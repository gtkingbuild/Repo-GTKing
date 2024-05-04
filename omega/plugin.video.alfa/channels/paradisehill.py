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
             'channel': 'paradisehill', 
             'host': config.get_setting("current_host", 'paradisehill', default=''), 
             'host_alt': ["https://en.paradisehill.cc/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "all/?sort=created_at"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "popular/?filter=month&sort=by_likes"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "actors/?sort=by_likes"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "studios/?sort=by_likes"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories/?sort=by_likes"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/?pattern=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='item')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.find('img')['src']
        title = elem.find('img')['alt']
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
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
    matches = soup.find_all('div', class_='item list-film-item')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.find('img', itemprop='image')['src']
        title = elem.img['alt']
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    num=1
    data = httptools.downloadpage(item.url).data
    pornstars = scrapertools.find_multiple_matches(data, '"/actor/\d+/">([^<]+)</a>')
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    if len(pornstars) <= 2:
        lista = item.contentTitle.split()
        lista.insert (0, pornstar)
        item.contentTitle = ' '.join(lista)
    patron = '{"src":"([^"]+)","type"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        url = url.replace("\\", "")
        title = "[COLOR yellow] Parte %s[/COLOR]" %num
        num +=1
        contentTitle = item.contentTitle + title
        itemlist.append(Item(channel=item.channel, action="play", title = title, contentTitle=contentTitle, url=url, plot=pornstar) )
    return itemlist

