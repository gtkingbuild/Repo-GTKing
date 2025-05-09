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
             'channel': 'plusone8', 
             'host': config.get_setting("current_host", 'plusone8', default=''), 
             'host_alt': ["https://plusone8.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# MP4 Error 403

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?orderby=longest"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars"))

    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "porn-categories"))
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
    soup = create_soup(item.url).find('main', id='main')
    matches = soup.find_all('article', id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        if "svg" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        # url = url.replace("?actors=","/star/")
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.parent.find_next_siblings("li")[0].a['href']
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
    soup = create_soup(item.url).find('main', id='main')
    matches = soup.find_all('article', class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        if "test" in url:
            continue
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        if ".gif" in thumbnail:
            thumbnail = elem.img['data-src']
        thumbnail += "|verifypeer=false"
        time = elem.find('span', class_='length')
        actors = elem['class']
        actriz = ""
        for x in actors:
            if not "actors-" in x:
                continue
            actor = x.replace("actors-", "").replace("-", " ")
            actriz += "%s & " %actor
        if actriz:
            title = "[COLOR cyan]%s[/COLOR] %s" %(actriz[:-2], title)
        if time:
            time = time.text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current')
    if next_page:
        next_page = next_page.parent.find_next_siblings("li")[0].a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('a', id='tracking-url')['href']
    url = url.replace(" ", "%20")
    itemlist.append(Item(channel=item.channel, action="play", contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = create_soup(item.url).find('a', id='tracking-url')['href']
    # url = url.replace(" ", "%20")
    # url += "|ignore_response_code=True" 
    # url += "|verifypeer=false" 
    # url += "|Referer=%s" % item.url
    itemlist.append(Item(channel=item.channel, action="play", contentTitle = item.title, url=url))
    return itemlist
