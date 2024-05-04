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
# https://letsjerk.tv https://letsjerk.to
canonical = {
             'channel': 'letsjerk', 
             'host': config.get_setting("current_host", 'letsjerk', default=''), 
             'host_alt': ["https://letsjerk.tv/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# No se ven thumbnail

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?order=newest"))
    itemlist.append(Item(channel=item.channel, title="Mas valorados" , action="lista", url=host + "?order=rating_month"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?order=views_month"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "?order=comments_month"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))

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
    matches = soup.find('div', class_='thumbs').find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='taxonomy-name').text.strip()
        thumbnail = ""
        cantidad = elem.find('div', class_='number').text.strip()
        title = "%s (%s)" % (title, cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail))
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
    matches = soup.find('div', class_='thumbs').find_all('li')
    for elem in matches:
        quality = ""
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        time = elem.find('em', class_='time_thumb').em#.text.strip()
        quality = elem.find('i', class_='quality')
        if quality:
            quality = "[COLOR red]HD[/COLOR]"
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s %s" % (time.text.strip(),quality,title)
        elif quality:
            title = "%s %s" % (quality,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle = title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='video-container')
    v1 = matches.find_all('source')
    v2 = matches.find('iframe')
    if v1:
        for elem in v1:
            quality = elem['title']
            url = elem['src']
            itemlist.append(Item(channel=item.channel, action="play", title=quality, url=url) )
    else:
        url = v2['src']
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.title, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='video-container')
    v1 = matches.find_all('source')
    v2 = matches.find('iframe')
    if v1:
        for elem in v1:
            quality = elem['title']
            url = elem['src']
            itemlist.append(['%sp' %quality, url])
            itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    else:
        url = v2['src']
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle= item.title, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
