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


''' CANAL ANTIGUA OUT pages
    gameofporn  veporns  https://www.veporno.net  https://www.fxporn.net      http://www.veporns.com    '''

#  https://veporn.com/  https://pornoflix.com/

canonical = {
             'channel': 'veporns', 
             'host': config.get_setting("current_host", 'veporns', default=''), 
             'host_alt': ["https://veporn.com/"], 
             'host_black_list': [], 
             'pattern': ['<div class="logo"><a href="([^"]+)" title="'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
# POST https://veporn.com/wp-admin/admin-ajax.php?action=action_load_video&offset=1 

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?order=newest&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="lista", url=host + "?order=views&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?order=rating&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "?order=comments&page=1"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "?order=longest&page=1"))
    
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "pornstar/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&order=newest&page=1" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='performer-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-original']
        cantidad = elem.find('span', class_='count')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url += "?order=newest&page=1"
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                            fanart=thumbnail, thumbnail=thumbnail ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_='taxonomy-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.find('div', class_='taxonomy-name').text.strip()
        thumbnail = elem.img['data-original']
        cantidad = elem.find('div', class_='number')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url += "?order=newest&page=1"
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                            fanart=thumbnail, thumbnail=thumbnail ))
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
    if "/star/" in item.url:
        matches = soup.find('div', class_='videos').find_all('li')
    else:
        matches = soup.find_all('li', class_='ficevi')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        time = elem.find('em', class_='time_thumb').text.strip()
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail ))
                             
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    else:
        next_page = soup.find('div', class_='loaders')
        current_page = scrapertools.find_single_match(item.url, "page=(\d+)")
        if not current_page:
            current_page = "1"
        if next_page:
            next_page = int(current_page) + 1
            next_page = re.sub(r"page=\d+", "page={0}".format(next_page), item.url)
            itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='player')
    url = soup.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    pornstars = soup.find_all('a', href=re.compile("/pornstar/[A-z0-9- ]+/"))
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR cyan]%s[/COLOR]" % pornstar
    plot = ""
    if len(pornstars) <= 4:
        lista = item.contentTitle.split()
        if "HD" in item.title:
            lista.insert (4, pornstar)
        else:
            lista.insert (2, pornstar)
        item.contentTitle = ' '.join(lista)
    else:
        plot = pornstar
    
    url = soup.find('div', class_='video-container').iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
