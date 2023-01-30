# -*- coding: utf-8 -*-
# -*- Channel Ievenn -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
from channels import filtertools
from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from channels import autoplay
from platformcode import config, logger
from channelselector import get_thumb

IDIOMAS = {'es': 'CAST', 'en': 'VO'}
list_idiomas = list(set(IDIOMAS.values()))

list_servers = ['okru', 'youtube']
list_quality = []

canonical = {
             'channel': 'ievenn', 
             'host': config.get_setting("current_host", 'ievenn', default=''), 
             'host_alt': ["https://ievenn.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host


def get_source(url, headers={}, post={}, soup=False, unescape=False):
    logger.info()

    if post:
        if soup:
            data = httptools.downloadpage(url, post=post, headers=headers, soup=True, canonical=canonical).soup
        else:
            data = httptools.downloadpage(url, post=post, headers=headers, canonical=canonical).data
    else:
        if soup:
            data = httptools.downloadpage(url, soup=True, headers=headers, canonical=canonical).soup
        else:
            data = httptools.downloadpage(url, headers=headers, canonical=canonical).data

        if unescape:
            data = scrapertools.unescape(data)

    return data


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(
        Item(
            action="sub_menu",
            channel=item.channel,
            thumbnail=get_thumb("cast", auto=True),
            title="Castellano"
        )
    )

    itemlist.append(
        Item(
            action="sub_menu",
            channel=item.channel,
            thumbnail=get_thumb("vo", auto=True),
            title="Idioma Original"
        )
    )

    itemlist.append(
        Item(
            action="search",
            channel=item.channel,
            thumbnail=get_thumb("search", auto=True),
            url=host + "?s=",
            title="Buscar..."
        )
    )

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    is_cast = False
    if item.title == "Castellano":
        url = host + "seccion/cine/cine-espanol/"
        is_cast = True
    else:
        url = host + "seccion/cine/cine-english/"

    itemlist.append(
        Item(
            action="list_all",
            channel=item.channel,
            thumbnail=get_thumb("All", auto=True),
            title="Todas",
            url=url
        )
    )

    itemlist.append(
        Item(
            action="genres",
            channel=item.channel,
            thumbnail=get_thumb("genres", auto=True),
            title="Generos",
            url=host,
            is_cast=is_cast
        )
    )

    return itemlist

def list_all(item):
    logger.info()

    itemlist = list()
    soup = get_source(item.url, soup=True)
    matches = soup.find_all("article")
    if not matches:
        return itemlist

    for elem in matches:
        url = elem.a["href"]
        thumb = "https:" + scrapertools.find_single_match(elem.a.get("style", ""), "url\(([^\)]+)\);")
        info = elem.find("h2").a.text.split(" – ")
        title = info[0]
        if len(info) == 3:
            year = info[1]
            lang = info[2][:2].lower()
        else:
            year = "-"
            lang = "es"

        contentTitle = re.sub("(year)", "", title).strip()

        new_item = Item(
            channel=item.channel,
            infoLabels={"year": year},
            thumbnail=thumb,
            title=title,
            contentTitle=contentTitle,
            url=url,
            language=IDIOMAS.get(lang.lower(), "LAT"),
            action="findvideos",
        )

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)
    try:
        next_page = soup.find("span", class_="current").find_next_sibling()["href"]

        itemlist.append(
            Item(
                channel=item.channel,
                title="Siguiente >>",
                url=next_page,
                action='list_all'
            )
        )
    except:
        pass

    return itemlist


def genres(item):
    logger.info()

    itemlist = list()
    if item.is_cast:
        soup = get_source(item.url, soup=True).find("li", id="menu-item-2407931")
    else:
        soup = get_source(item.url, soup=True).find("li", id="menu-item-2407932")

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text

        itemlist.append(
            Item(
                action="list_all",
                channel=item.channel,
                title=title,
                url=url
            )
        )

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    infoLabels = item.infoLabels
    url = get_source(item.url, soup=True).find("iframe").get("src", "")

    if not url.startswith("http"):
        url = "https:" + url
    itemlist.append(
        Item(
            action='play',
            channel=item.channel,
            infoLabels=infoLabels,
            language=item.language,
            url=url,
            title="%s"
        )
    )

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and (
            not item.videolibrary or item.extra != 'findvideos'):
        itemlist.append(
            Item(
                action="add_pelicula_to_library",
                contentTitle=item.contentTitle,
                channel=item.channel,
                extra="findvideos",
                title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                url=item.url
            )
        )

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            item.search = True
            return list_all(item)
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
            item.url = host + "seccion/cine/cine-espanol/"
        elif categoria == 'latino':
            item.url = host + "idioma/latino/"
        elif categoria == 'castellano':
            item.url = host + "idioma/castellano"
        elif categoria == 'infantiles':
            item.url = host + 'animacion'
        elif categoria == 'terror':
            item.url = host + 'terror'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist