# -*- coding: utf-8 -*-
# -*- Channel SleazeMovies -*-
# -*- Created for Alfa-addon -*-
# -*- By Sculkurt -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from bs4 import BeautifulSoup

# http://www.eroti.ga/  https://www.sleazemovies.com/  https://erotiga.net/

canonical = {
             'channel': 'sleazemovies', 
             'host': config.get_setting("current_host", 'sleazemovies', default=''), 
             'host_alt': ["https://erotiga.net/"], 
             'host_black_list': ["https://www.eroti.ga/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = list()
    itemlist.append(item.clone(title="Todas", action="lista", url=host +"page/2/", thumbnail=get_thumb('all', auto=True)))
    itemlist.append(item.clone(title="Generos", action="genero", url=host, thumbnail=get_thumb('genres', auto=True)))
    itemlist.append(item.clone(title="Buscar", action="search", thumbnail=get_thumb('search', auto=True)))
    return itemlist


def search(item, texto):
    logger.info()
    if texto != "":
        texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host, texto)
    item.extra = "busqueda"
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def genero(item):
    logger.info()
    itemlist = list()
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all('li', class_='cat-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        itemlist.append(Item(channel=item.channel, action='lista', title=title, url=url))
    return itemlist


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    if post:
        data = httptools.downloadpage(url, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all("article", class_=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.h2.a['href']
        title = elem.h2.text.strip()
        title = title.replace("&#8217;", "'")
        thumbnail = elem.find('div', class_='twp-article-post-thumbnail').img['src']
        if "gif" in thumbnail:
            thumbnail = elem.find('div', class_='twp-article-post-thumbnail').img['data-src']
        contentTitle = scrapertools.find_single_match(title, '([^\(]+)')
        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year:
            year = scrapertools.find_single_match(title, '\((\d{4})\)')
        title = "%s (%s)" %(contentTitle, year)
        if not year:
            year = "-"
        plot = elem.p.text.strip()
        itemlist.append(Item(channel=item.channel, action = "findvideos", title = title, contentTitle = contentTitle, url = url,
                             thumbnail = thumbnail, plot=plot, contentType = "movie", infoLabels = {'year': year}))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb = True)

    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item): 
    logger.info() 
    itemlist = [] 
    data = httptools.downloadpage(item.url, canonical=canonical).data 
    id = scrapertools.find_single_match(data, 'src=".*?vid=([^"]+)"').replace("amp;", "")
    logger.debug(data)
    post = "vid=%s&alternative=sleazyvids&ord=0" % id
    url = "%splayer/ajax_sources.php" %host
    data = httptools.downloadpage(url, post=post, canonical=canonical).data
    url = scrapertools.find_single_match(data, '"file":"([^"]+)"').replace("\/", "/").replace(" ", "%20")
    title = scrapertools.find_single_match(data, '"label":"([^"]+)"').replace("\/", "/").replace(" ", "%20")
    itemlist.append(Item(channel=item.channel, action="play", title=title, contentTitle = item.title, url=url))
    
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(item.clone(title = '[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url = item.url,
                             action = "add_pelicula_to_library",
                             extra = "findvideos",
                             contentTitle = item.contentTitle,
                             thumbnail = item.thumbnail))
    return itemlist 

