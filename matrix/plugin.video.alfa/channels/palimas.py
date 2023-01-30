# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re
from bs4 import BeautifulSoup

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from channels import autoplay

list_quality = []
list_servers = ['mixdrop']

canonical = {
             'channel': 'palimas', 
             'host': config.get_setting("current_host", 'palimas', default=''), 
             'host_alt': ["https://palimas.org/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?view=latest&when=this-month"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?view=most-viewed&when=this-month"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?view=top-rated&when=this-month"))
    itemlist.append(Item(channel=item.channel, title="1080-4K" , action="lista", url=host + "?view=1080p-4k&when=this-month"))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "channels"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars?view=top-rated"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?q=%s" % (host,texto)
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
    if "/channels" in item.url:
        matches = soup.find_all('div', class_='channel-cube')
    else:
        matches = soup.find_all('div', class_='catt')
    if "/pornstars" in item.url:
        matches = soup.find_all('div', class_='pornstar-cube')
    for elem in matches:
        url = elem.a['href']
        thumbnail = elem.img['src']
        stitle = elem.find('h2').text
        cantidad = elem.find('h3').text
        title = "%s (%s)" % (stitle,cantidad)
        plot = ""
        url = urlparse.urljoin(host,url)
        thumbnail = urlparse.urljoin(host,thumbnail)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page =""
    pages = soup.find('div', class_='pagination')
    if pages:
        pages = pages.find_all('a')[-1]
        next_page = pages['href']
    if next_page:
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
    matches = soup.find_all('div', class_='video-cube')
    for elem in matches:
        stime = elem.find('div', class_='vmin').text
        quality = elem.find('div', class_='vquality').text
        url = elem.a['href']
        stitle = elem.img['alt']
        thumbnail = elem.img['src']
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (stime,quality,stitle)
        plot = ""
        url = urlparse.urljoin(host,url)
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot,))
    next_page =""
    pages = soup.find('div', class_='pagination')
    if pages.a:
        pages = pages.find_all('a')[-1]
        next_page = pages['href']
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<option value="(\d+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for player in matches:
        post = "&video-player=%s" % player
        data = httptools.downloadpage(item.url, post = post).data
        url = scrapertools.find_single_match(data, ".src = '([^']+)'")
        if url and not url.startswith("http"):
            url = "https:%s" % url
        if "api.gounlimited" in url:
            continue
        if url =="https:h":
            continue

        if not url:
            continue
        itemlist.append(Item(channel=item.channel, action="play", title="%s", contentTitle=item.title, url=url))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

