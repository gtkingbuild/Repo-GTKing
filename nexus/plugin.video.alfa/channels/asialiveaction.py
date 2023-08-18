# -*- coding: UTF-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re

from modules import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from lib import jsunpack
from platformcode import config, logger

canonical = {
             'channel': 'asialiveaction', 
             'host': config.get_setting("current_host", 'asialiveaction', default=''), 
             'host_alt': ["https://asialiveaction.com"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

IDIOMAS = {"Esp": "CAST", "Lat": "LAT", "Sub": "VOSE"}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['gvideo', 'openload','streamango']


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="lista", title="Peliculas",
                             url=urlparse.urljoin(host, "/peliculas/"), type='pl'))
    itemlist.append(Item(channel=item.channel, action="lista", title="Series",
                         url=urlparse.urljoin(host, "/series-tv/"), type='sr'))
    itemlist.append(Item(channel=item.channel, action="submenu", title="Idioma",
                         url=urlparse.urljoin(host, "/peliculas/"), cat='genre'))
    # itemlist.append(Item(channel=item.channel, action="lista", title="Anime",
                             # url=urlparse.urljoin(host, "/anime/")))
    itemlist.append(Item(channel=item.channel, action="category", title="Géneros",
                         url=urlparse.urljoin(host, "/peliculas/"), cat='genre'))
    itemlist.append(Item(channel=item.channel, action="category", title="Calidad",
                         url=urlparse.urljoin(host, "/peliculas/"), cat='quality'))
    itemlist.append(Item(channel=item.channel, action="category", title="Orden Alfabético",
                         url=urlparse.urljoin(host, "/peliculas/"), cat='abc'))
    itemlist.append(Item(channel=item.channel, action="category", title="Año de Estreno",
                         url=urlparse.urljoin(host, "/peliculas/"), cat='year'))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host+"/?s="))
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def submenu(item):
    logger.info()
    itemlist = list()
    itemlist.append(Item(channel=item.channel, action="lista", title="Castellano",
                             url=urlparse.urljoin(host, "/audio-espanol/")))
    itemlist.append(Item(channel=item.channel, action="lista", title="Latino",
                             url=urlparse.urljoin(host, "/audio-latino/")))
    return itemlist



def category(item):
    logger.info()
    itemlist = list()
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    action = "lista"
    if item.cat == 'abc':   
        data = scrapertools.find_single_match(data, '<ul class="AZList">(.+?)</ul>')
        action = "lista_a"
    elif item.cat == 'genre':
        data = scrapertools.find_single_match(data, '>Géneros</div>(.+?)</ul>')
    elif item.cat == 'year':
        data = scrapertools.find_single_match(data, '>Año</div>(.+?)</ul>')
    elif item.cat == 'quality':
        data = scrapertools.find_single_match(data, '>Calidad</div>(.+?)</ul>')
    if item.cat == 'abc':
        patron = '<li><a href="([^"]+)".*?>([^<]+)<' 
    else:
        patron = '<li.*?>([^<]+)<a href="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for title,scrapedurl in matches:
        if item.cat == 'abc':
            title1=scrapedurl
            scrapedurl = title
            title = title1
        if title != 'Próximas Películas':
            if not scrapedurl.startswith("http"): scrapedurl = host + scrapedurl
            itemlist.append(item.clone(action=action, title=title, url=scrapedurl, type='cat'))
    return itemlist


def search_results(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron = '<span class=.post-labels.>([^<]+)</span>.*?class="poster-bg" src="([^"]+)"/>.*?<h4>.*?'
    patron +=">(\d{4})</a>.*?<h6>([^<]+)<a href='([^']+)"
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedtype, scrapedthumbnail, scrapedyear, scrapedtitle ,scrapedurl in matches:
        title="%s [%s]" % (scrapedtitle, scrapedyear)
        new_item= Item(channel=item.channel, title=title, url=scrapedurl, thumbnail=scrapedthumbnail)
        if scrapedtype.strip() == 'Serie':
            new_item.contentSerieName = scrapedtitle
            new_item.action = 'episodios'
            new_item.type = 'sr'
        else:
            new_item.contentTitle = scrapedtitle
            new_item.action = 'findvideos'
            new_item.type = 'pl'
        itemlist.append(new_item)
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def episodios(item):
    logger.info()
    itemlist = list()
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '<a href="([^"]+)" target="_blank" class="fa fa-download".*?'
    patron += 'Episodio ([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedepi in matches:
        title="1x%s - %s" % (scrapedepi, item.contentSerieName)
        #urls = scrapertools.find_multiple_matches(scrapedurls, 'href="([^"]+)')
        scrapedthumbnail = ""
        itemlist.append(item.clone(action='findvideos', title=title, url=scrapedurl, thumbnail=scrapedthumbnail, type=item.type,
                                   infoLabels=item.infoLabels))
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]",
                             url=item.url, action="add_serie_to_library", extra="episodios",
                             contentSerieName=item.contentSerieName))
    return itemlist


def lista_a(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    patron  = '(?is)MvTbImg">.*?href="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?>.*?'
    patron += '<strong>([^<]+)<.*?'
    patron += 'href.*?>([^<]+)<.*?'
    patron += 'href.*?>([^"]+)<\/a>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedtype, scrapedyear in matches:
        if not scrapedthumbnail.startswith("http"): scrapedthumbnail = "https:" + scrapedthumbnail
        new_item = Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail,
                       type=scrapedtype, infoLabels={'year':scrapedyear})
        if 'Movie' in scrapedtype:
            new_item.contentTitle = scrapedtitle
            new_item.action = 'findvideos'
        else :
            new_item.contentSerieName = scrapedtitle
            new_item.action = 'episodios'
            
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    #pagination
    url_next_page = scrapertools.find_single_match(data, 'class="next page-numbers" href="([^"]+)"')
    if len(itemlist)>0 and url_next_page:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='lista_a'))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    patron  = '(?is)class="TPost C">.*?href="([^"]+)".*?' #scrapedurl
    patron += 'src="([^"]+)".*?>.*?' #scrapedthumbnail
    patron += '(?:T|t)itle">([^<]+)<.*?' #scrapedtitle
    patron += '(?:Y|y)ear">([^<]+)<.*?' #scrapedyear
    patron += 'class="Genre">(.*?)</p' #scrapedtype
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear, scrapedtype in matches:
        if not scrapedthumbnail.startswith("http"): scrapedthumbnail = "https:" + scrapedthumbnail
        title="%s - %s" % (scrapedtitle,scrapedyear)
        scrapedtype = scrapertools.find_multiple_matches(scrapedtype, 'internal">([^<]+)<')
        type = scrapedtype[0]
        language = []
        for elem in scrapedtype:
            if "Latino" in elem: lang = "Lat"
            elif "Español" in elem: lang = "Esp"
            else: lang = "Sub"
            language.append(IDIOMAS.get(lang, lang))
        new_item = Item(channel=item.channel, title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                       type=scrapedtype, language=language, infoLabels={'year':scrapedyear})
        if 'Movie' in type:
            new_item.contentTitle = scrapedtitle
            new_item.action = 'findvideos'
        else :
            new_item.contentSerieName = scrapedtitle
            new_item.action = 'episodios'
            
        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    #pagination
    url_next_page = scrapertools.find_single_match(data, 'class="next page-numbers" href="([^"]+)"')
    if len(itemlist)>0 and url_next_page:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='lista'))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    if not "/paste/" in item.url:
        data = httptools.downloadpage(item.url, canonical=canonical).data.replace("&quot;",'"').replace("amp;","").replace("#038;","")
        url = scrapertools.find_single_match(data, '<span><a rel="nofollow" target="_blank" href="([^"]+)"')
        data = httptools.downloadpage(url).data
    else:
        data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, 'var videos([A-z]{3}) = \[([^<]+)</script>')
    for lang, bloque in matches:
        lang = IDIOMAS.get(lang, lang)
        matches  = scrapertools.find_multiple_matches(bloque, "(http.*?)'")
        for url in matches:
            itemlist.append(item.clone(action = "play", title = "%s", language=lang, url = url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
