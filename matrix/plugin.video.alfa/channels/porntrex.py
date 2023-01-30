# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido
    import urllib

import re

from core import httptools
from core.item import Item
from core import scrapertools
from core import servertools
from platformcode import config, logger

canonical = {
             'channel': 'porntrex', 
             'host': config.get_setting("current_host", 'porntrex', default=''), 
             'host_alt': ["https://www.porntrex.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             # 'pattern': ['<link href="([^"]+)" rel="canonical"'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="lista", title="Nuevos Vídeos", url=host + "latest-updates/"))
    itemlist.append(item.clone(action="lista", title="Mejor Valorados", url=host + "top-rated/"))
    itemlist.append(item.clone(action="lista", title="Más Vistos", url=host + "most-popular/"))
    itemlist.append(item.clone(action="categorias", title="Modelos", url=host + "models/?sort_by=avg_videos_popularity"))
    itemlist.append(item.clone(action="categorias", title="Canal", url=host + "channels/"))
    itemlist.append(item.clone(action="categorias", title="Listas", url=host + "playlists/"))
    itemlist.append(item.clone(action="categorias", title="Categorías", url=host + "categories/?sort_by=title"))
    itemlist.append(item.clone(title="Buscar...", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    item.url = "%ssearch/%s/latest-updates/" % (host, texto.replace(" ", "-"))
    item.extra = texto
    try:
        return lista(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = get_data(item.url)
    data = scrapertools.find_single_match(data, '<div class="main-container">(.*?)</html>')
    # Extrae las entradas
    if "/channels/" in item.url:
        patron = '<div class="video-item   ">.*?<a href="([^"]+)" title="([^"]+)".*?src="([^"]+)".*?<li>([^<]+)<'
    elif "/playlists/" in item.url:
        patron = '<div class="item ">.*?<a href="([^"]+)" title="([^"]+)".*?data-original="([^"]+)".*?<div class="totalplaylist">([^<]+)<'
    else:
        patron = '<a class="item" href="([^"]+)" title="([^"]+)".*?src="([^"]+)".*?<div class="videos">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail, videos in matches:
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        if not scrapedthumbnail.startswith("https"):
            scrapedthumbnail = "https:%s" % scrapedthumbnail
            scrapedthumbnail = scrapedthumbnail.replace(" " , "%20")
        scrapedthumbnail += "|Referer=%s" % host
        if videos:
            scrapedtitle = "%s  (%s)" % (scrapedtitle, videos)
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                                   fanart=scrapedthumbnail))
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if "#" in next_page:
        next_page = scrapertools.find_single_match(data, '<li class="next">.*?data-parameters="([^"]+)">')
        next_page = next_page.replace(":", "=").replace(";", "&").replace("+from_albums", "")
        next_page = "?%s" % next_page
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def get_data(url_orig):
    try:
        # if config.get_setting("url_error", "porntrex"):
            # raise Exception
        response = httptools.downloadpage(url_orig, canonical=canonical)
        if not response.data or "urlopen error [Errno 1]" in str(response.code):
            raise Exception
    except:
        # config.set_setting("url_error", True, "porntrex")
        import random
        server_random = ['nl', 'de', 'us']
        server = server_random[random.randint(0, 2)]
        url = "https://%s.hideproxy.me/includes/process.php?action=update" % server
        post = "u=%s&proxy_formdata_server=%s&allowCookies=1&encodeURL=0&encodePage=0&stripObjects=0&stripJS=0&go=" \
               % (urllib.quote(url_orig), server)
        while True:
            response = httptools.downloadpage(url, post, follow_redirects=False)
            if response.headers.get("location"):
                url = response.headers["location"]
                post = ""
            else:
                break
    return response.data


def lista(item):
    logger.info()
    itemlist = []
    # data = get_data(item.url)
    data = httptools.downloadpage(item.url, canonical=canonical).data
    # if config.get_setting("menu_info", "porntrex"):
        # action = "menu_info"
    # Quita las entradas, que no son private <div class="video-preview-screen video-item thumb-item private "
    if "playlists" in item.url:
        patron = '<div class="video-item item  ".*?'
    else:
        patron = '<div class="video-preview-screen video-item thumb-item  ".*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)"\s*alt="([^"]+)".*?'
    patron += '<span class="quality">([^<]+)<.*?'
    patron += '</i>([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, quality, duration in matches:
        if not scrapedthumbnail.startswith("https"):
            scrapedthumbnail = "https:%s" % scrapedthumbnail
        scrapedthumbnail += "|Referer=%s" % host
        scrapedtitle = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (duration, quality, scrapedtitle)
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, 
                                   fanart=scrapedthumbnail, contentTitle = scrapedtitle))
    # Extrae la marca de siguiente página
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if "#" in next_page:
        next_page = scrapertools.find_single_match(data, '<li class="next">.*?data-parameters="([^"]+)">')
        next_page = next_page.replace(":", "=").replace(";", "&").replace("+from_albums", "")
        next_page = "?%s" % next_page
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
