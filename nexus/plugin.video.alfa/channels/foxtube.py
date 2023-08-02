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


#  https://www.foxtube.com   https://www.muyzorras.com
canonical = {
             'channel': 'foxtube', 
             'host': config.get_setting("current_host", 'foxtube', default=''), 
             'host_alt': ["https://www.foxtube.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Ultimos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Mejor valorados" , action="lista", url=host + "/video/top/"))
    itemlist.append(Item(channel=item.channel, title="Mas largos" , action="lista", url=host + "/video/long/"))
    itemlist.append(Item(channel=item.channel, title="Recomendados" , action="lista", url=host + "/video/recommended/"))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + 'pornstars-search/'))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + 'channels/'))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%stags/%s" % (host, texto)
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
    matches = soup.find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        cantidad = elem.find_all('span')[-1]
        if cantidad:
            cantidad = cantidad.text.strip().replace(" Videos", "").replace(" videos", "")
            title = "%s (%s)" %(title,cantidad)
        url = urlparse.urljoin(item.url,url)
        thumbnail += "|referer=%s" %host
        plot = ""
        if "channels" in item.url:
            action = "canal"
        else:
            action = "lista"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('div', class_='pagi').span.find_next_sibling("a")
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    item.id = soup.find('div', class_='scmt')['data-obj']
    item.canal = scrapertools.find_single_match(item.url, 'channels/([A-z-]+)')
    item.url = "%susers/get/%s/videos/1/" % (host,id)
    return lista(item)


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('ul', id='m6').find_all('li')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        plot = ""
        thumbnail = ""
        scrapedurl = urlparse.urljoin(item.url,url)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail, plot=plot) )
    return itemlist


def create_soup(url, post=None, unescape=False):
    logger.info()
    if post:
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = httptools.downloadpage(url, post=post, headers=headers, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    if "users" in item.url:
        post = {'path': '%s' %item.canal, 'order_vid': 'uv'} 
        soup = create_soup(item.url, post=post)
    else:
        soup = create_soup(item.url)
    matches = soup.find('div', class_='ltv').find_all('article')
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='rh').find_all('span')[-1].text.strip()
        quality = elem.find('span', class_='rh').find_all('span')[0].text.strip()
        canal = elem.find('span', class_='itb').text.strip()
        if quality:
           
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] [COLOR cyan]%s[/COLOR] %s" % (time,quality,canal,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] [COLOR cyan]%s[/COLOR] %s" % (time,canal,title)
        url = urlparse.urljoin(item.url,url)
        thumbnail += "|referer=%s" %host
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel = item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                             fanart=thumbnail, contentTitle=title, plot=plot))
    next_page = soup.find('div', class_='pg')
    if next_page and next_page.span.find_next_sibling('a'):
        next_page = next_page.span.find_next_sibling('a')['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    # soup = create_soup(item.url)
    data = httptools.downloadpage(url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    elem = soup.find('section', class_='vg')
    url = elem.find('a', class_='th_if')['href']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    # soup = create_soup(item.url)
    data = httptools.downloadpage(url).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    elem = soup.find('section', class_='vg')
    url = elem.find('a', class_='th_if')['href']
    pornstars = elem.find_all('a', class_='tp')
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "cyan]%s[/COLOR]" % pornstar
    canal = elem.find_all('a', class_='icn')
    for x , value in enumerate(canal):
        canal[x] = value.text.strip()
    canal = ' | '.join(canal)
    pornstar = "%s [%s]" %(pornstar,canal)
    lista = item.contentTitle.split()
    if "HD" in item.contentTitle:
        lista[5]= pornstar
    else:
        lista[3]= pornstar
    item.contentTitle = ' '.join(lista)    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist