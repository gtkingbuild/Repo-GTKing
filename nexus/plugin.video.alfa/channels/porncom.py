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
import base64

canonical = {
             'channel': 'porncom', 
             'host': config.get_setting("current_host", 'porncom', default=''), 
             'host_alt': ["https://www.porn.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host + "sites"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%svideos/search?q=%s" % (host,texto)
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
    matches = soup.find_all('div', class_='list-global__item')
    for elem in matches:
        elem = elem.find('a', class_=False)
        url = elem['href']
        if "Categorias" in item.title:
            url += "?ad=30"
        title = elem.img['alt']
        thumbnail = elem.img['data-src']
        cantidad = elem.find('div', class_='list-global__details')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    if "Categorias" in item.title:
        itemlist.sort(key=lambda x: x.title)
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
    soup = create_soup(item.url).find('main', class_='container-fluid')
    matches = soup.find_all('div', class_='list-global__item')
    for elem in matches:
        if elem.has_attr('data-adch'):
            continue
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='list-global__duration').text.strip()
        server = elem.find('div', class_='list-global__details').a.text.strip()
        title = "[COLOR yellow]%s[/COLOR] [%s] %s" % (time, server, title)
        url = scrapertools.find_single_match(url,'.*?5odHRwczov([^/]+)/\d+/\d+')
        url = url.replace("%3D", "=").replace("%2F", "/")
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


# https://porntop.com/video/238835/deepika-bernie-svintis-our-boobs-are-the-same/
# https://ebonyo.com/black-chick-with-big-boobs-tori-taylor-riding-white-man/             <iframe src= BASE64

# https://www.jacquieetmichelelite.com/film-porno/elite/8211/sans-tabou-ni-retenue.html   https://www.jacquieetmichelelite.com/es/pelicula-porno/elite/8211/sin-tabu-ni-moderacion.html

# https://ebonyo.com/ebony-yoga-girl-banged-hard-on-the-floor/
# <div class="responsive-player">
    # <iframe src="https://ebonyo.com/wp-content/plugins/clean-tube-player/public/player-x.php?q=cG9zdF9pZD0yMjcmdHlwZT1pZnJhbWUmdGFnPSUzQ2lmcmFtZSUyMHNyYyUzRCUyMmh0dHBzJTNBJTJGJTJGd3d3Lnh2aWRlb3MuY29tJTJGZW1iZWRmcmFtZSUyRjMxNTk4NzIxJTIyJTIwZnJhbWVib3JkZXIlM0QlMjIwJTIyJTIwd2lkdGglM0QlMjI1MTAlMjIlMjBoZWlnaHQlM0QlMjI0MDAlMjIlMjBzY3JvbGxpbmclM0QlMjJubyUyMiUyMGFsbG93ZnVsbHNjcmVlbiUzRCUyMmFsbG93ZnVsbHNjcmVlbiUyMiUyMHNhbmRib3glM0QlMjJhbGxvdy1zYW1lLW9yaWdpbiUyMGFsbG93LXNjcmlwdHMlMjIlM0UlM0MlMkZpZnJhbWUlM0U=" frameborder="0" scrolling="no" allowfullscreen></iframe>			</div>

# <div class="responsive-player">
    # <iframe src="https://lezvids.com/wp-content/plugins/clean-tube-player/public/player-x.php?q=cG9zdF9pZD00MzY1OSZ0eXBlPWlmcmFtZSZ0YWc9JTNDaWZyYW1lJTIwc3JjJTNEJTIyaHR0cHMlM0ElMkYlMkZlbWJlZC5yZWR0dWJlLmNvbSUyRiUzRmlkJTNEMzk0NjYyODElMjIlMjBmcmFtZWJvcmRlciUzRCUyMjAlMjIlMjB3aWR0aCUzRCUyMjY0MCUyMiUyMGhlaWdodCUzRCUyMjM2MCUyMiUyMHNjcm9sbGluZyUzRCUyMm5vJTIyJTIwYWxsb3dmdWxsc2NyZWVuJTIwc2FuZGJveCUzRCUyMmFsbG93LXNhbWUtb3JpZ2luJTIwYWxsb3ctc2NyaXB0cyUyMiUzRSUzQyUyRmlmcmFtZSUzRQ==" frameborder="0" scrolling="no" allowfullscreen></iframe>        </div>


# https://ebonyo.com/round-ass-ebony-roomie-sits-on-cock-instantly/
# <div class="responsive-player">
    # <iframe width="1280" height="720" src="https://www.pornestro.com/embed/775" frameborder="0" allowfullscreen sandbox="allow-same-origin allow-scripts"></iframe>			</div>


def findvideos(item):
    logger.info()
    itemlist = []
    url = base64.b64decode(item.url).decode("utf8")
    if not url.startswith("https"):
        url = "https:/%s" % url
    if "vid.com/v/" in url:
        url = httptools.downloadpage(url).url
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = base64.b64decode(item.url).decode("utf8")
    if not url.startswith("https"):
        url = "https:/%s" % url
    if "vid.com/v/" in url:
        url = httptools.downloadpage(url).url
    if "pornhat" in url:
        url = url.replace("video", "embed")
        data =  httptools.downloadpage(url).data
        url = scrapertools.find_single_match(data, '<link href="([^"]+)"')
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

