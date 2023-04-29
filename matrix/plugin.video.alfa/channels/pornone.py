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
             'channel': 'pornone', 
             'host': config.get_setting("current_host", 'pornone', default=''), 
             'host_alt': ["https://pornone.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Hetero" , action="submenu", url=host, pornstars = True))
    itemlist.append(Item(channel=item.channel, title="Female" , action="submenu", url=host + "female/"))
    itemlist.append(Item(channel=item.channel, title="Shemale" , action="submenu", url=host + "shemale/"))
    itemlist.append(Item(channel=item.channel, title="Gay" , action="submenu", url=host + "gay/"))
    return itemlist

def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=item.url + "newest/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=item.url + "views/month/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=item.url + "rating/month/"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=item.url + "comments/month/"))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=item.url + "longest/month/"))
    if item.pornstars: 
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars/"))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=item.url + "categories/"))
        itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url))
    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch?q=%s&sort=newest&page=1" % (item.url,texto)
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
    if "pornstars" in item.url:
        matches = soup.find('main').find_all('a', class_='tracking-tighter')
    else:
        matches = soup.find('main').find_all('a', class_='overflow-hidden')
    for elem in matches:
        url = elem['href']
        title = elem.img['alt'].replace('Video category ', '')
        if "pornstars" in item.url:
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.img['data-src']
        cantidad = elem.find('span', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        url += "newest/"
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    if not "pornstars" in item.url:
        itemlist.sort(key=lambda x: x.title)
    next_page = soup.find('a', title='Next Page')
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
    matches = soup.find_all('a', class_='relative')
    for elem in matches:
        url = elem['href']
        if "/cam/" in url:
            continue
        title = elem.find('img', class_='imgvideo')['alt']
        thumbnail = elem.find('img', class_='imgvideo')['src']
        time = elem.find('span', class_='text-f13')
        quality = time.find('img', alt='HD Video')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time.text.strip(),title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text.strip(),title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', title='Next Page')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    if "search" in item.url:
        next_page = soup.find('span', title='Next Page')
        if next_page:
            # page = scrapertools.find_single_match(item.url, '(.*?)&page=')
            next_page = next_page['onclick']
            next_page = re.sub("\D", "", next_page)
            next_page = re.sub(r"&page=\d+", "&page={0}".format(next_page), item.url)
            # next_page = "%s&page=%s" %(page, next_page)
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