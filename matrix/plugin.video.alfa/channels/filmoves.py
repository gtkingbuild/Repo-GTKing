# -*- coding: utf-8 -*-
# -*- Channel Filmoves -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
from core import tmdb
from core import httptools
from core.item import Item
from core import scrapertools
from core import servertools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


IDIOMAS = {'lat': 'LAT', 'cast': 'CAST', 'sub': 'VOSE'}
list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'fembed',
    'streamtape',
    'uqload',
    'streamsb',
    'mixdrop'
    ]

canonical = {
             'channel': 'filmoves', 
             'host': config.get_setting("current_host", 'filmoves', default=''), 
             'host_alt': ["https://filmoves.net/"], 
             'host_black_list': ["https://www.filmoves.net/", "https://filmoves.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    # autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Series', url=host + 'series', action='list_all',
                         thumbnail=get_thumb('tvshows', auto=True)))



    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + 'suggest?que=',
                         thumbnail=get_thumb("search", auto=True)))

    #
    # autoplay.show_option(item.channel, itemlist)

    return itemlist



def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Todas', action='list_all', url=host + "peliculas",
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Generos', action='section',
                         thumbnail=get_thumb('genres', auto=True)))

    return itemlist

def section(item):
    logger.info()

    itemlist = list()
    soup = create_soup(host)

    matches = soup.find("ul", class_="generos-menu")

    for elem in matches.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text

        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="main-peliculas")[-1].find_all("div", class_="movie-box-1")

    for elem in matches:

        thumb = elem.a.figure.img["src"]
        title = elem.a.p.text
        url = elem.a["href"]
        year = elem.a.span.text

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

        if "serie/" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.contentType = 'tvshow'
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"
            new_item.contentType = 'movie'

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    #try:
    url_next_page = soup.find("ul", class_="pagination").find_all("li")[-1].a["href"]
    #except:
    #    return itemlist

    if url_next_page:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    matches = create_soup(item.url).find_all("ul", id=re.compile("season-\d+"))

    infoLabels = item.infoLabels

    for elem in matches:

        season = elem["id"].split("-")[1]
        title = "Temporada %s" % season
        infoLabels["season"] = season

        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseasons',
                             context=filtertools.context(item, list_language, list_quality), infoLabels=infoLabels, 
                             contentType='season'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

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

    itemlist = list()
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    
    soup = create_soup(item.url).find("ul", id=re.compile("season-%s"  % season))
    matches = soup.find_all("article")
    
    for elem in matches:
        url = elem.a["href"]
        try:
            infoLabels["episode"] = int(elem.div.span.text.split("x")[1])
        except:
            infoLabels["episode"] = 1
        title = "%sx%s" % (season, infoLabels["episode"])

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             infoLabels=infoLabels, contentType='episode'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url, canonical=canonical).data
    matches = re.compile("(?i)video\[(\d+)\]\s+?=\s+?'.*?src=\"([^\"]+)\"", re.DOTALL).findall(data)

    if not matches:
        return itemlist
    for v_id, url in matches:

        lang_data = scrapertools.find_single_match(data, '<a href="#option%s">([^<]+)</a>' % v_id)

        if "lat" in lang_data.lower():
            lang = "LAT"
        elif "cast" in lang_data.lower():
            lang = "CAST"
        else:
            lang = "VOSE"

        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url, language=lang,
                             infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        item.url += texto + "&_token=ghukxZv83wiTlOeWadvNcAwot6a77zvDSt26FPvm"
        if texto != '':
            return search_results(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def search_results(item):
    logger.info()

    itemlist = list()
    data = httptools.downloadpage(item.url, headers={"x-requested-with": "XMLHttpRequest"}, add_referer=True, canonical=canonical).json

    for mit in data["data"]["m"]:
        url = mit["slug"]
        thumb = mit["cover"]
        title = mit["title"]
        year = mit["release_year"]
    
        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, contentTitle=title,
                             action="findvideos", contentType='movie', infoLabels={'year': year}))

    for sit in data["data"]["s"]:
        url = sit["slug"]
        thumb = sit["cover"]
        title = sit["title"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, contentSerieName=title,
                             action="seasons", contentType='tvshow'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria in ['peliculas', 'latino']:
            item.url = host + 'peliculas'
        elif categoria == 'infantiles':
            item.url = host + 'genero/animacion/'
        elif categoria == 'terror':
            item.url = host + 'genero/terror/'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
