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

# babestube
def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="submityourflicks" , action="submenu", host= "https://www.submityourflicks.com", thumbnail= "https://www.submityourflicks.com/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="interracial" , action="submenu", host= "https://www.interracial.com", thumbnail = "https://www.interracial.com/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="feetporno" , action="submenu", host= "https://www.feetporno.com", thumbnail = "https://www.feetporno.com/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="chubbyporn" , action="submenu", host= "https://www.chubbyporn.com", thumbnail = "https://www.chubbyporn.com/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="cartoonporn" , action="submenu", host= "https://www.cartoonporn.com", thumbnail = "https://www.cartoonporn.com/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="trannylime" , action="submenu", host= "https://www.trannylime.com", thumbnail = "https://www.trannylime.com/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="gotgayporn" , action="submenu", host= "https://www.gotgayporn.com", thumbnail = "https://www.gotgayporn.com/images/logo.png"))
    return itemlist

def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=item.host + "/latest-updates/?sort_by=post_date&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=item.host + "/most-popular/?sort_by=video_viewed_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=item.host + "/top-rated/?sort_by=rating_month&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=item.host + "/longest/?sort_by=duration&from=1"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=item.host + "/categories/?sort_by=title"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.host))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/%s/?sort_by=post_date&from_videos=1" % (item.url,texto)
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
    matches = soup.find_all('div', class_='thumb grid item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.img:
            thumbnail = elem.img['data-src']
        else:
            thumbnail = ""
        cantidad = elem.find('span', class_='col')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url += "?sort_by=post_date&from=1"
        title = title.replace("Hardcore ", "")
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='videos_list').find_all('div', class_='item thumb')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        if elem.img:
            thumbnail = elem.img['data-src']
        else:
            thumbnail = ""
        time = elem.find('div', class_='time').text.strip()
        quality = elem.find('span', class_='label hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='item active')
    if next_page and next_page.find_next_sibling("li"):
        next_page = next_page.find_next_sibling("li").a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
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
