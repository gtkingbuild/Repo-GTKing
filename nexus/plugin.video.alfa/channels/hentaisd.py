# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core import scrapertools
from core.item import Item
from core import servertools
from platformcode import config, logger
from channels import filtertools
from modules import autoplay
from lib import jsunpack

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = ['default']
list_servers = ['sharedvid']

# http://hentaisd.tv  http://hentaird.tv/
canonical = {
             'channel': 'hentaisd', 
             'host': config.get_setting("current_host", 'hentaisd', default=''), 
             'host_alt': ["https://hentaisd.tv"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, action="lista", title="Estrenos", url=host + "/hentai/estrenos/"))
    itemlist.append(Item(channel=item.channel, action="series", title="Todos", url=host + "/hentai/"))
    itemlist.append(Item(channel=item.channel, action="series", title="Sin Censura", url=host + "/hentai/sin-censura/"))
    itemlist.append(Item(channel=item.channel, action="generos", title="Por géneros", url=host + "/hentai/generos/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/buscar/?t=%s" % (host, texto)
    try:
        return series(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<h3 class="media-heading"><a href="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, title in matches:
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="col-sm-6 col-md-2 central">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<h5>([^<]+)</h5>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(Item(channel=item.channel, action="episodios", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def series(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="media">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '>([^<]+)</p>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,plot in matches:
        url=scrapedurl
        title=scrapedtitle
        thumbnail=scrapedthumbnail
        itemlist.append(Item(channel=item.channel, action="episodios", title=title, contentTitle = title, url=url,
                             thumbnail=thumbnail, fanart=thumbnail, plot=plot))
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="series", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li><a href="([^"]+)".*?'
    patron += 'Capitulo (\d+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl,title in matches:
        title = title + " - " + item.title
        url = scrapedurl
        thumbnail = item.thumbnail
        plot = item.plot
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle = title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail, plot=plot))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>||<br/>', "", data)
    data = scrapertools.find_single_match(data, 'var videos =(.*?)\}')
    patron = 'src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        url = url.replace("cloud/index.php", "cloud/query.php")
        if "/player.php" in url:
            data = httptools.downloadpage(url, canonical=canonical).data
            phantom = scrapertools.find_single_match(data, 'Phantom.Start\("(.*?)"\)')
            phantom = phantom.replace('"+"', '')
            import base64
            packed = base64.b64decode(phantom).decode("utf8")
            unpacked = jsunpack.unpack(packed)
            url = scrapertools.find_single_match(unpacked, '"src","([^"]+)"')
            if not url.startswith("https"):
                url = "https:%s" % url
        itemlist.append(Item(channel=item.channel, title="%s", url=url, action='play', language='VO',contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    return itemlist
