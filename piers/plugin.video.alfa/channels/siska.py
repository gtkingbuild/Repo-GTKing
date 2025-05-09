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
from core import servertools
from core.item import Item
from core import httptools
# from channels import filtertools
from modules import autoplay

# IDIOMAS = {'vo': 'VO'}
# list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['gounlimited']

canonical = {
             'channel': 'siska', 
             'host': config.get_setting("current_host", 'siska', default=''), 
             'host_alt': ["http://siska.video/"], 
             'host_black_list': [], 
             'pattern': ['itemprop="?url"?\s*content="?([^"|\s*]+)["|\s*]'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

##### MUCHO NETU

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "best_xvideos.php?views=month"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "chanells.php"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "category.php"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch.php?s=%s&search=search" % (host, texto)
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
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="back">.*?'
    patron += 'href="([^"]+)" class="">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                              thumbnail="" , plot=scrapedplot) )
    return sorted(itemlist, key=lambda i: i.title)


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data = scrapertools.find_single_match(data,'<h1 class=(.*?)<div id="footer"')
    patron = 'href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'title">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("Watch Channel ", "")
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                              thumbnail=thumbnail , plot=scrapedplot) )
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li class=\'pure-u-1-3.*?'
    patron += '<a title=\'[^\']+\' href=\'([^\']+)\'.*?'
    patron += 'duration\'>([^<]+)<.*?'
    patron += 'data-src=\'([^\']+)\'.*?'
    patron += 'alt=\'([^\']+)\''
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtime,scrapedthumbnail,scrapedtitle in matches:
        scrapedtime = scrapedtime.replace("Duration: ", "").replace(" : ", ":")
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (scrapedtime, scrapedtitle)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, plot=plot,
                              fanart=thumbnail, contentTitle = title))
                              
                              
    next_page = scrapertools.find_single_match(data, 'href="([^"]+)">Next')
    if next_page == "":
        next_page = scrapertools.find_single_match(data, '<a href=\'([^\']+)\' title=\'Next Page\'>')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    patron = '<iframe src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        if not ".xyz" in url:
            itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play', contentTitle = item.contentTitle))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

