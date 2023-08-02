# -*- coding: utf-8 -*-
# -*- Channel SeriesRetro -*-
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

list_idiomas = ['LAT']
list_servers = ['okru', 'yourupload', 'mega']
list_quality = []

canonical = {
             'channel': 'seriesretro', 
             'host': config.get_setting("current_host", 'seriesretro', default=''), 
             'host_alt': ["https://seriesretro.com/", "https://pelisretro.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def get_source(url, soup=False, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer':referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def mainlist(item):
    logger.info()
    
    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    """itemlist.append(
        Item(
            action = "sub_menu",
            channel = item.channel,
            thumbnail = get_thumb("movies", auto=True),
            title = "Peliculas",
            viewType = "videos"
        )
    )"""

    itemlist.append(
        Item(
            action = "sub_menu",
            channel = item.channel,
            thumbnail = get_thumb("tvshows", auto=True),
            title = "Series",
            viewType = "videos"
        )
    )

    itemlist.append(
        Item(
            action = "search",
            channel = item.channel,
            thumbnail = get_thumb("search", auto=True),
            title = "Buscar..."
        )
    )

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()
    global host

    if item.title == "Peliculas":
        host = canonical['host_alt'][1]
    else:
        host = canonical['host_alt'][0]


    itemlist = list()

    itemlist.append(
        Item(
            action = "list_all",
            channel = item.channel,
            thumbnail = get_thumb("All", auto=True),
            title = "Todas",
            url = host + ("lista-series/" if item.title == "Series" else "peliculas/")
        )
    )

    if item.title == "Series":
        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                thumbnail = get_thumb("animacion", auto=True),
                title = "Animación",
                url = host + "category/animacion/"
            )
        )

    itemlist.append(
        Item(
            action = "section",
            channel = item.channel,
            thumbnail = get_thumb("genres", auto=True),
            title = "Generos",
            url = host
        )
    )

    itemlist.append(
        Item(
            action = "section",
            channel = item.channel,
            thumbnail = get_thumb("alphabet", auto=True),
            title = "Alfabetico",
            url = host
        )
    )

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()
    
    soup = get_source(item.url, soup=True)
    
    matches = soup.find("ul", class_="MovieList NoLmtxt Rows AX A06 B04 C03 E20")

    if not matches:
        return itemlist

    for elem in soup.find_all("article"):

        url = elem.a["href"]
        title = elem.a.h3.text
        thumb = elem.find("img")
        thumb = thumb["data-src"] if thumb.has_attr("data-src") else thumb["src"]
        year = elem.find("span", class_="Year").text

        new_item = Item(
                        channel = item.channel,
                        infoLabels={"year": year or '-'},
                        thumbnail = thumb,
                        title = title,
                        url = url
                    )

        if "pelisretro" in url:
            new_item.contentTitle = title
            new_item.action = "findvideos"
            new_item.contentType = 'movie'
        else:
            new_item.contentSerieName = title
            new_item.action = "seasons"
            new_item.contentType = 'tvshow'

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        next_page = soup.find("a", class_="next page-numbers")["href"]

        itemlist.append(
            Item(
                channel = item.channel,
                title = "Siguiente >>",
                url = next_page,
                action = 'list_all'
            )
        )
    except:
        pass

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    if item.title == "Generos":
        soup = get_source(item.url, soup=True).find("ul", class_="sub-menu")
        action = "list_all"
    elif item.title == "Alfabetico":
        soup = get_source(item.url, soup=True).find("ul", class_="AZList")
        action = "alpha_list"

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text

        itemlist.append(
            Item(
                action = action,
                channel = item.channel,
                title = title,
                url = url
            )
        )

    return itemlist


def alpha_list(item):
    logger.info()

    itemlist = list()

    soup = get_source(item.url, soup=True).find("tbody")
    
    if not soup:
        return itemlist
    for elem in soup.find_all("tr"):
        info = elem.find("td", class_="MvTbTtl")
        thumb = elem.find("td", class_="MvTbImg").a.img["src"]
        url = info.a["href"]
        title = info.a.text.strip()

        itemlist.append(
            Item(
                action = 'seasons',
                channel = item.channel,
                contentSerieName = title,
                contentType = 'tvshow', 
                thumbnail = thumb,
                title = title,
                url = url
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()
    infoLabels = item.infoLabels

    soup = get_source(item.url, soup=True).find_all("div", class_="Wdgt AABox")

    for elem in soup:
        try:
            season = int(elem.find("div", class_="AA-Season")["data-tab"])
        except:
            season = 1
        title = "Temporada %s" % season
        infoLabels["season"] = season
        
        itemlist.append(
            Item(
                action = 'episodesxseason',
                channel = item.channel,
                infoLabels=infoLabels,
                contentType = 'season', 
                title = title,
                url = item.url
            )
        )

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and not (item.videolibrary or item.extra):
        itemlist.append(
            Item(
                action = "add_serie_to_library",
                channel = item.channel,
                contentType = "tvshow",
                contentSerieName = item.contentSerieName,
                extra = "episodios",
                title = '[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                url = item.url
            )
        )

    return itemlist


def episodios(item):
    logger.info()

    itemlist = list()
    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    soup = get_source(item.url, soup=True).find_all("div", class_="Wdgt AABox")
    infoLabels = item.infoLabels
    season = infoLabels["season"]

    for elem in soup:
        if elem.find("div", class_="AA-Season")["data-tab"] == str(season):
            epi_list = elem.find_all("tr")
            for epi in epi_list:
                try:
                    url = epi.a["href"]
                    try:
                        epi_num = int(epi.find("span", class_="Num").text)
                    except:
                        epi_num = 1
                    epi_name = epi.find("td", class_="MvTbTtl").a.text
                    infoLabels["episode"] = epi_num
                    title = "%sx%s - %s" % (season, epi_num, epi_name)

                    itemlist.append(
                        Item(
                            action = "findvideos",
                            channel = item.channel,
                            infoLabels = infoLabels,
                            contentType = "episode",
                            title = title,
                            url = url,
                        )
                    )
                except:
                    pass
            break
    
    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    infoLabels = item.infoLabels
    
    soup = get_source(item.url, soup=True).find("ul", class_="TPlayerNv").find_all("li")

    for btn in soup:
        opt = btn["data-tplayernv"]
        srv = btn.span.text.lower()
        if "opci" in srv.lower():
            srv = "okru"
            # continue
        
        itemlist.append(
            Item(
                action = 'play',
                channel = item.channel,
                infoLabels = infoLabels,
                language = 'LAT',
                opt = opt,
                server = srv,
                title = srv,
                url = item.url
            )
        )

    itemlist = sorted(itemlist, key=lambda i: i.server)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if item.contentType != "episode":
        if config.get_videolibrary_support() and len(itemlist) > 0 and (not item.videolibrary or item.extra != 'findvideos'):
            itemlist.append(
                Item(
                    action = "add_pelicula_to_library",
                    contentTitle = item.contentTitle,
                    channel = item.channel,
                    extra = "findvideos",
                    title = '[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                    url = item.url
                )
            )

    return itemlist


def play(item):
    logger.info()
    
    itemlist = list()

    soup = get_source(item.url, soup=True).find("div", class_="TPlayerTb", id=item.opt)
    
    url = scrapertools.find_single_match(str(soup), 'src="([^"]+)"')
    url = re.sub("amp;|#038;", "", url)
    
    url = get_source(url, soup=True).find("div", class_="Video").iframe["src"]
    
    item.url = url
    item.server = ""
    
    itemlist.append(item)
    
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    
    search_result = list()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':

            item.url = 'https://seriesretro.com/' + "?s="
            item.url += texto
            search_result = list_all(item)

            item.url = 'https://pelisretro.com/' + "?s="
            item.url += texto
            search_result.extend(list_all(item))

            return search_result
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
