# -*- coding: utf-8 -*-
# -*- Channel SeriesKao -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import base64

from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from lib import jsunpack
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay


IDIOMAS = {'2': 'VOSE', "0": "LAT", "1": "CAST"}

list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'gvideo',
    'fembed',
    'directo'
    ]

canonical = {
             'channel': 'serieskao', 
             'host': config.get_setting("current_host", 'serieskao', default=''), 
             'host_alt': ["https://serieskao.org/"], 
             'host_black_list': ["https://serieskao.net/"], 
             'pattern': ['<link\s*rel="shortcut\s*icon"\s*href="(\w+\:\/\/[^\/]+\/)'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Todas', action='list_all', url=host + "peliculas",
                         thumbnail=get_thumb('movies', auto=True), type="pelicula"))
    itemlist.append(Item(channel=item.channel, title='Por Género', action='genres', url=host,
                         thumbnail=get_thumb('movies', auto=True), type="pelicula"))
    itemlist.append(Item(channel=item.channel, title='Estrenos', action='list_all', url=host + "lanzamiento/2022",
                         thumbnail=get_thumb('movies', auto=True), type="pelicula"))
    itemlist.append(Item(channel=item.channel, title='Series', url=host + 'series', action='list_all',
                         thumbnail=get_thumb('tvshows', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist

def genres(item):
    logger.info()
    itemlist = list()
    existe = []
    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, '(?is)href="(/genero[^"]+)">([^<]+)')
    for url, title in matches:
        if title in existe: continue
        existe.append(title)
        itemlist.append(Item(channel=item.channel, title=title, url=host + url,
                 action="list_all"))
    return itemlist
    

def get_language(lang_data):
    logger.info()

    language = list()

    lang_list = lang_data.find_all("span", class_="flag")
    for lang in lang_list:
        lang = scrapertools.find_single_match(lang["style"], r'/flags/(.*?).png\)')
        if lang == 'en':
            lang = 'vose'
        if lang not in language:
            language.append(lang)
    return language


def list_all(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data
    if item.extra == "buscar":
        patron  = '(?is)><article>.*?img src="([^"]+).*?'
        patron += 'alt="([^"]+).*?'
        patron += 'href="([^"]+).*?'
        patron += 'class="year">([^<]+)'
    else:
        patron  = '(?is)><article id="post.*?img src="([^"]+).*?'
        patron += 'alt="([^"]+).*?'
        patron += 'href="([^"]+).*?'
        patron += 'class="imdb">.*?<span>([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for thumb, title, url, year in matches:
        title = title.replace("#038","")
        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

        if "series/" in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.context = filtertools.context(item, list_language, list_quality)
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = scrapertools.find_single_match(data, '"next" href="([^"]+)')
    except:
        return itemlist

    if url_next_page:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()
    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, "(?is)class='title'>([^<]+)")
    infoLabels = item.infoLabels

    for title in matches:
        season = scrapertools.find_single_match(title, '\d+')
        infoLabels["season"] = season

        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseasons',
                             infoLabels=infoLabels))

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

    data = httptools.downloadpage(item.url).data
    season = item.infoLabels["season"]
    patron  = "(?is)class='numerando'>(%s - \d+)<.*?" %season
    patron += "href='([^']+)'"
    patron += ">([^<]+)"
    matches = scrapertools.find_multiple_matches(data, patron)

    infoLabels = item.infoLabels

    for episode, url, epi_name in matches:
        epi_num = scrapertools.find_single_match(episode, "- (\d+)")
        infoLabels["episode"] = epi_num
        title = "%sx%s - %s" % (season, epi_num, epi_name)

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    data = httptools.downloadpage(item.url).data
    patron  = "'dooplay_player_option' data-type='([^']+).*?"
    patron += "data-post='([^']+).*?"
    patron += "data-nume='([^']+).*?"
    dtype, dpost, dnume = scrapertools.find_single_match(data, patron)
    post = {"action": "doo_player_ajax", "post": dpost, "nume": dnume,
           "type": dtype}
    headers = {"Referer": item.url}
    doo_url = "%swp-admin/admin-ajax.php" % host
    data = httptools.downloadpage(doo_url, post=post, headers=headers).json
    url = data["embed_url"]
    data = httptools.downloadpage(url).data
    matches = scrapertools.find_multiple_matches(data, "go_to_player\('([^']+)")
    for url in matches:
        if not url.startswith("http"):
            uu = "https://api.mycdn.moe" + "/player/?id=%s" %url
            ddd = httptools.downloadpage(uu).data
            url = scrapertools.find_single_match(ddd, 'iframe src="([^"]+)')
        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url,
                                     infoLabels=item.infoLabels))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

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
        item.url = item.url + texto
        item.extra = "buscar"

        if texto != '':
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()

    item = Item()
    try:
        if categoria in ['peliculas']:
            item.url = host + 'pelicula'
        elif categoria == 'infantiles':
            item.url = host + 'pelicula/filtro/?genre=animacion-2'
        elif categoria == 'terror':
            item.url = host + 'pelicula/filtro/?genre=terror-2/'
        item.first = 0
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
