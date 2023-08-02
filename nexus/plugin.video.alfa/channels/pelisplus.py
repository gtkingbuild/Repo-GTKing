# -*- coding: utf-8 -*-
# -*- Channel Pelisplus -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re, base64

from channels import autoplay
from channels import filtertools
from core import httptools
from core import jsontools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channelselector import get_thumb
from lib import generictools

IDIOMAS = {'latino': 'LAT', 'castellano': 'CAST', 'subtitulado': 'VOSE'}
list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'directo',
    'vidlox',
    'fembed',
    'uqload',
    'gounlimited',
    'fastplay',
    'mixdrop',
    'mystream'
    ]

canonical = {
             'channel': 'pelisplus', 
             'host': config.get_setting("current_host", 'pelisplus', default=''), 
             'host_alt': ["https://pelisplus.lat"], 
             'host_black_list': ["https://home.pelisplus.lat/", 
                                 "https://pelisplus.mov/", "https://pelisplus.ninja/", "https://www.pelisplus.lat/", 
                                 "https://www.pelisplus.me/", "https://pelisplushd.net/","https://pelisplushd.to/"], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
domain = scrapertools.find_single_match(host, patron_domain)


def mainlist(item):
    logger.info()
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Peliculas", action="sub_menu", url_todas = "listado-peliculas", 
                         url_populares = "/tendencias/dia",
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Series", action="sub_menu", url_todas = "listado-series",
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Anime", action="sub_menu", url_todas ="ver-animes",
                         thumbnail=get_thumb('anime', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Doramas", action="list_all", url=host + "doramas",
                         content="serie", thumbnail=get_thumb('doramas', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host + '?s=',
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()
    itemlist = list()

    if item.title.lower() == "anime":
        content = item.title.lower()
        item.title = "Animes"
    else:
        content = item.title.lower()[:-1]

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + item.url_todas,
                         thumbnail=get_thumb('all', auto=True)))

    if item.title.lower() == "peliculas":
        itemlist.append(Item(channel=item.channel, title="Ultimos populares", action="list_all",
                            url=host + item.url_todas + item.url_populares,
                            thumbnail=get_thumb('more watched', auto=True), type=content))
        itemlist.append(Item(channel=item.channel, title="Peliculas estreno", action="list_all",
                            url=host + item.url_todas + '/estrenos',
                            thumbnail=get_thumb('more watched', auto=True), type=content))
        itemlist.append(Item(channel=item.channel, title="Generos", action="section",
                             thumbnail=get_thumb('genres', auto=True), type=content))
    elif item.title.lower() == "series":
        itemlist.append(Item(channel=item.channel, title="Ultimos estrenos", action="list_all",
                             url=host + 'series-de-estreno', thumbnail=get_thumb('more watched', auto=True), type=content))
        itemlist.append(Item(channel=item.channel, title="Mas Vistas", action="list_all",
                             url=host + 'series-populares', thumbnail=get_thumb('more watched', auto=True), type=content))
    return itemlist


def list_all(item):
    logger.info()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '(?is)card-body.*?Page navigation example')
    patron  = '(?is)<a class="Posters-link" href="([^"]+).*?'
    patron += 'srcSet="([^"]+).*?'
    patron += '<p> <!-- -->([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, thumb, title in matches:
        year = scrapertools.find_single_match(title, r"(\d{4})")
        if not year:
            year = "-"
        if item.type and item.type.lower() not in url:
            continue
        new_item = Item(channel=item.channel, title=title, url=host + url, thumbnail=thumb, infoLabels={"year": year})

        if "/pelicula/" in url:
            new_item.contentTitle = title
            new_item.action = "findvideos"
            new_item.contentType = 'movie'
        else:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.contentType = 'tvshow'

        itemlist.append(new_item)
    tmdb.set_infoLabels_itemlist(itemlist, True)
    #  Paginación

    try:
        #next_page = scrapertools.find_single_match(data, 'href="([^"]+)"><i class="ic-chevron-right"></i>')
        #next_page = scrapertools.find_single_match(data, '<div\s*class="nav-links">.*?<a\s*class="page-link\s*current".*?''<a\s*class="page-link"[^>]*href="([^"]+)"')
        next_page = scrapertools.find_single_match(data, '<div\s*class="nav-links">.*?<a\s*class="next page-numbers" href="([^"]+)"')
        

        if next_page:
            if not next_page.startswith(host):
                next_page = host + next_page
            itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()
    data = httptools.downloadpage(item.url).data
    patron  = 'data-toggle="tab"[^>]*.?[^<]+<!-- -->([^<])+'
    infoLabels = item.infoLabels
    matches = scrapertools.find_multiple_matches(data, patron)
    
    for title in matches:
        title = "Temporada " + title
        infoLabels["season"] = scrapertools.find_single_match(title, "Temporada (\d+)")
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseasons',
                             infoLabels=infoLabels, contentType='season'))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

    return itemlist


def episodesxseasons(item):
    logger.info()
    data = httptools.downloadpage(item.url).data
    itemlist = list()
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    patron  = '(%sepisodio.*?temporada-%s[^"]+).*?' %(host, item.contentSeason)
    patron += 'btn-block">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    if not matches:
        patron  = '(%sepisodio/.*?%sx[^"]+).*?' %(host, item.contentSeason)
        patron += 'btn-block">([^<]+)'
        matches = scrapertools.find_multiple_matches(data, patron)
    if not matches:
        return itemlist

    for url, episodio in matches:
        epi_num = scrapertools.find_single_match(episodio, "E(\d+)")
        epi_name = scrapertools.find_single_match(episodio, ":([^$]+)")
        infoLabels['episode'] = epi_num
        title = '%sx%s - %s' % (season, epi_num, epi_name.strip())

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos', infoLabels=infoLabels, contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    return itemlist


def section(item):
    logger.info()
    itemlist = list()
    data = httptools.downloadpage(host).data
    bloque = scrapertools.find_single_match(data, "Generos(.*?)side-nav-header")
    patron  = '<a href="([^"]+)">'
    patron += '([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, title in matches:
        itemlist.append(Item(channel=item.channel, url=host + url, title=title, action='list_all', type=item.type))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url, forced_proxy_opt='ProxyCF', canonical=canonical)
    
    json = scrapertools.find_single_match(data.data, '(?is)type="application/json">(.*?)</script>')
    
   
    json1 = jsontools.load(json)["props"]["pageProps"]["thisMovie"]["videos"]

    for idioma in json1:
        for videos in json1[idioma]:
            url = videos["result"]
                
            if u"player.php" in url:
                data = httptools.downloadpage(url).data
                url = scrapertools.find_single_match(data, "var url = '([^']+)'")
            itemlist.append(Item(channel=item.channel, title='%s [%s]', url=url, action='play', language=idioma,
                infoLabels=item.infoLabels))
    

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % (i.server.capitalize(), i.language))

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if item.contentType == 'movie':
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(Item(channel=item.channel,
                                 title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                                 url=item.url,
                                 action="add_pelicula_to_library",
                                 extra="findvideos",
                                 contentTitle=item.contentTitle))
    return itemlist


def play(item):
    logger.info()
    if "cinestart" in item.url:
        id = scrapertools.find_single_match(item.url, "id=(\w+)")
        token = scrapertools.find_single_match(item.url, "token=(\w+)")
        post = {"id" : id, "token" : token}
        dd = httptools.downloadpage("https://cinestart.streams3.com/r.php", post = post, allow_redirect=False).url
        v = scrapertools.find_single_match(dd, "t=(\w+)")
        dd = httptools.downloadpage("https://cinestart.net/vr.php?v=%s" %v).json
        item.url = dd["file"]
    if "apialfa.tomatomatela.com" in item.url:
        data = httptools.downloadpage(item.url).data
        hostx = "https://apialfa.tomatomatela.com/ir/"
        item.url = hostx + scrapertools.find_single_match(data, 'id="link" href="([^"]+)')
        data = httptools.downloadpage(item.url).data
        xvalue = scrapertools.find_single_match(data, 'name="url" value="([^"]+)')
        post = {"url" : xvalue}
        item.url = httptools.downloadpage(hostx + "rd.php", follow_redirects=False, post=post).headers.get("location", "")
        data = httptools.downloadpage("https:" + item.url).data
        xvalue = scrapertools.find_single_match(data, 'name="url" value="([^"]+)')
        post = {"url" : xvalue}
        item.url = httptools.downloadpage(hostx + "redirect_ddh.php", follow_redirects=False, post=post).headers.get("location", "")
        hash = scrapertools.find_single_match(item.url,"#(\w+)")
        file = httptools.downloadpage("https://tomatomatela.com/details.php?v=%s" %hash).json
        item.url = file["file"]
        dd = httptools.downloadpage(item.url, only_headers=True).data
    return [item]


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url += texto

    try:
        if texto != '':
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria in ['peliculas', 'latino']:
            item.url = host + 'peliculas/estrenos'
        elif categoria == 'infantiles':
            item.url = host + 'generos/animacion/'
        elif categoria == 'terror':
            item.url = host + 'generos/terror/'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
