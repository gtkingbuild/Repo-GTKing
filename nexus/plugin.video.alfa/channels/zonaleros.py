# -*- coding: utf-8 -*-
# -*- Channel ZonaLeros -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    from urllib.parse import unquote
else:
    from urllib import unquote

import re
from bs4 import BeautifulSoup
import codecs
import base64

from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools
from modules import autoplay

IDIOMAS = {'la': 'Latino'}
list_language = list(set(IDIOMAS.values()))

list_quality = []

list_servers = [
    'gvideo',
    'fembed'
    ]

canonical = {
             'channel': 'zonaleros', 
             'host': config.get_setting("current_host", 'zonaleros', default=''), 
             'host_alt': ["https://www.zona-leros.com/"], 
             'host_black_list': ["https://www.zonaleros.org/", "https://www.zona-leros.net/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': 'ProxyCF', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu',
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + 'search?q=',
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.title == "Peliculas":
        url = host + "peliculazl-free"
    elif item.title == "Series":
        url = host + "series"

    itemlist.append(Item(channel=item.channel, title='Ultimas', url=url, action='list_all',
                         thumbnail=get_thumb('last', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Generos', action='section', url=url,
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Por Año', action='section', url=url,
                         thumbnail=get_thumb('year', auto=True)))

    return itemlist


def create_soup(url, post=None, unescape=False):
    logger.info()

    if post:
        data = httptools.downloadpage(url, post=post, add_referer=True, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def section(item):
    logger.info()

    itemlist = list()
    soup = create_soup(host + "peliculazl-free")

    if item.title == "Generos":
        matches = soup.find("select", id="genre_select").find_all("option")
        base_url = "%s?generos[]=%s&order=created"
    else:
        matches = soup.find("select", id="year_select").find_all("option")
        base_url = "%s?year[]=%s&order=created"

    for elem in matches:
        url = base_url % (item.url, elem["value"])
        title = elem.text
        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("ul", class_="ListAnimes")

    if not matches:
        return itemlist

    for block in matches:
        data = block.find_all("li")
        for elem in data:
            url = elem.a["href"]
            if "juegos-" in url:
                continue
            info = elem.find("div", class_="Description")
            thumb = elem.img.get("src", "")
            title = info.strong.text
            year = scrapertools.find_single_match(codecs.encode(info.text, "utf-8"), "del año (\d{4})")
            if not year:
                try:
                    year = scrapertools.find_single_match(codecs.encode(info.text, "utf-8"), "\d+ de \w+ de (\d{4})")
                    if not year: year = "-"
                except:
                    year = "-"
            new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, infoLabels={"year": year})

            if "serie" in url:
                new_item.contentSerieName = title.strip()
                new_item.action = "seasons"
                new_item.contentType = 'tvshow'
                new_item.context = filtertools.context(item, list_language, list_quality)
            else:
                new_item.contentTitle = title.strip()
                new_item.action = "findvideos"
                new_item.contentType = 'movie'

            itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", rel="next")["href"]
    except:
       return itemlist

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find_all("div", id=re.compile("temp-\d+"))
    infoLabels = item.infoLabels

    for elem in matches:
        season = scrapertools.find_single_match(elem["id"], "-(\d+)")
        title = "Temporada %s" % season
        infoLabels["season"] = season

        itemlist.append(Item(channel=item.channel, title=title, action='episodesxseasons', url=item.url,
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    itemlist = itemlist[::-1]

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 contentSeason=item.contentSeason))

    return itemlist


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)
    for tempitem in templist:
        itemlist.extend(episodesxseasons(tempitem))

    return itemlist


def episodesxseasons(item):
    logger.info()

    itemlist = list()

    infoLabels = item.infoLabels
    season = infoLabels["season"]

    soup = create_soup(item.url).find("div", id="temp-%s" % season)
    matches = soup.find_all("li")

    for elem in matches:
        url = elem.a["href"]
        title = elem.find("span", class_="Capi").text
        epi_num = title.split("x")[1]
        infoLabels["episode"] = epi_num

        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos',
                             infoLabels=infoLabels, contentType = 'episode'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    if "episode" not in item.url:
        base_url = "%sapi/calidades" % host
        soup = create_soup(item.url)
        tk = soup.find("meta", attrs={"name": "csrf-token"}).get("content", "")
        id_list = soup.find_all("span", id=re.compile("value-"))

        for id_value in id_list:
            c_id = id_value["data-value"]
            post = {"calidad_id": c_id, "_token": tk}
            data = httptools.downloadpage(base_url, post=post).data
            url_list = scrapertools.find_multiple_matches(data, r'\?hs=([^"]+)')
    else:
        data = httptools.downloadpage(item.url, canonical=canonical).data
        data = data.replace("'", '"')
        url_list = scrapertools.find_multiple_matches(data, r'\?hs=([^"]+)')

    for url in url_list:
        if not url.startswith("http"):
            url = unquote(base64.b64decode(codecs.decode(url, "rot13")).decode('utf-8'))
        if "fembed" in url:
            srv = "Fembed"
        else:
            srv = ""
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action="play", infoLabels=item.infoLabels,
                             language="lat", server=srv))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.servers.capitalize())

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def play(item):
    logger.info()

    if item.server == "Fembed":
        hash = scrapertools.find_single_match(item.url, "h=([^$]+)")
        base_url = "https://api.zona-leros.net/fembed/api.php"
        item.url = httptools.downloadpage(base_url, post= {"h": hash}).json['url']

    return [item]


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.type = "search"
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
        if categoria in ['peliculas', 'latino']:
            item.url = host + "peliculazl-free"
        elif categoria == 'infantiles':
            item.url = host + 'peliculas/genero/animacion'
        elif categoria == 'terror':
            item.url = host + 'peliculas/genero/terror'

        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
