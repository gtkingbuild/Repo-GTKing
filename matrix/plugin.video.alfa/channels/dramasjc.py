# -*- coding: utf-8 -*-
# -*- Channel DramasJC -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channels import autoplay
from channels import filtertools
from bs4 import BeautifulSoup

IDIOMAS = {'Su': 'VOSE', 'La': 'Lat', 'Es': 'CAST', 'Ca': 'Cast', 'VO':'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['okru', 'mailru', 'openload']

canonical = {
             'channel': 'dramasjc', 
             'host': config.get_setting("current_host", 'dramasjc', default=''), 
             'host_alt': ["https://www.doramasjc.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()
    itemlist.append(Item(channel=item.channel, title="Doramas", action="menu_doramas",
                         thumbnail=get_thumb('doramas', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", url=host+'peliculas/',
                         type='movie', thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host+'?s=',
                               thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def menu_doramas(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todos", action="list_all", url=host + 'series',
                         thumbnail=get_thumb('all', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb('genres', auto=True)))

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


def list_all(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)
    matches = soup.find("ul", class_="MovieList NoLmtxt Rows AX A06 B04 C03 E20")

    if not matches:
        return itemlist

    for elem in soup.find_all("article"):

        url = elem.a["href"]
        title = elem.a.h3.text
        thumb = elem.find("img")
        thumb = thumb["data-src"] if thumb.has_attr("data-src") else thumb["src"]
        year = elem.find("span", class_="Year").text

        new_item = Item(channel=item.channel, url=url, title=title, thumbnail=thumb, infoLabels={"year": year})

        if "movie" not in url:
            new_item.contentSerieName = title
            new_item.action = "seasons"
        else:
            new_item.contentTitle = title
            new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        next_page = soup.find("a", class_="next page-numbers")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("li", class_ ="menu-category")

    for elem in soup.find_all("li"):
        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find_all("div", class_="Wdgt AABox")

    infoLabels = item.infoLabels
    for elem in soup:
        season = elem.find("div", class_="AA-Season")["data-tab"]
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseason',
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and not item.extra:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName
                             ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find_all("div", class_="Wdgt AABox")
    infoLabels = item.infoLabels
    season = infoLabels["season"]

    for elem in soup:
        if elem.find("div", class_="AA-Season")["data-tab"] == str(season):
            epi_list = elem.find_all("tr")
            for epi in epi_list:
                try:
                    url = epi.a["href"]
                    epi_num = epi.find("span", class_="Num").text
                    epi_name = epi.find("td", class_="MvTbTtl").a.text
                    infoLabels["episode"] = epi_num
                    title = "%sx%s - %s" % (season, epi_num, epi_name)

                    itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                         infoLabels=infoLabels))
                except:
                    pass
            break
    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url).find("ul", class_="TPlayerNv").find_all("li")
    infoLabels = item.infoLabels
    for btn in soup:
        opt = btn["data-tplayernv"]
        info = btn.find_all("span")
        srv = info[0].text
        lang = info[1].text[2]

        if "opci" in srv.lower():
            # srv = "okru"
            continue
        itemlist.append(Item(channel=item.channel, title=srv, url=item.url, action='play', server=srv, opt=opt,
                             language=IDIOMAS.get(lang, "VOSE"), infoLabels=infoLabels))

    itemlist = sorted(itemlist, key=lambda i: i.server)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def play(item):
    logger.info()
    itemlist = list()

    soup = create_soup(item.url).find("div", class_="TPlayerTb", id=item.opt)
    url = scrapertools.find_single_match(str(soup), 'src="([^"]+)"')
    url = re.sub("amp;|#038;", "", url)
    url = create_soup(url).find("div", class_="Video").iframe["src"]
    itemlist.append(item.clone(url=url, server=""))
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return list_all(item)
    else:
        return []


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas']:
            item.url = host+'peliculas/'

        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
