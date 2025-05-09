# -*- coding: utf-8 -*-
# -*- Channel CineHindi -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
from bs4 import BeautifulSoup

from core import tmdb
from core import httptools
from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools
from modules import autoplay

IDIOMAS = {"Subtitulado": "VOSE"}
list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'gvideo',
    'fembed'
    ]

canonical = {
             'channel': 'cinehindi', 
             'host': config.get_setting("current_host", 'cinehindi', default=''), 
             'host_alt': ["https://cinehindi.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Novedades', url=host, action='list_all',
                         thumbnail=get_thumb('newest', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Estrenos', url='%sgenero/estreno/' % (host),
                         action='list_all', thumbnail=get_thumb('premieres', auto=True)))

    itemlist.append(
        Item(channel=item.channel, title='Generos', action='section', thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Por Año', action='section',
                         thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True),  extra='movie'))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def create_soup(url, post=None, unescape=False):
    logger.info()

    if post:
        data = httptools.downloadpage(url, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup



def section(item):
    logger.info()

    itemlist = list()

    soup = create_soup(host)

    if item.title == "Generos":
        matches = soup.find("section", id="categories-3")
    else:
        matches = soup.find("section", id="torofilm_movies_annee-3")

    for elem in matches.find_all("li"):

        url = elem.a["href"]
        title = elem.a.text
        itemlist.append(Item(channel=item.channel, title=title, action="list_all", url=url))

    if item.title == "Generos":
        return itemlist

    return itemlist[::-1]


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("section", class_="section movies")
    if not matches:
        matches = soup.find("div", id="aa-movies")
    for elem in matches.find_all("article", class_=re.compile(r"post (?:dfx|fcl|movies)")):

        url = elem.a["href"]


        title = elem.h2.text
        thumb = elem.img["src"]

        year = "-"
        
        try:
            year = elem.find("span", class_="year").text
        except:
            pass

        stitle = title

        if not config.get_setting('unify'):
            title += "[COLOR grey] (%s)[/COLOR]" % year

        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, language="VOSE",
                             infoLabels={"year": year}, contentTitle=stitle, action="findvideos"))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        url_next_page = soup.find("a", text="SIGUIENTE")["href"]
    except:
        return itemlist

    itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all', type=item.type))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)
    matches = soup.find("ul", class_="aa-tbs aa-tbs-video").find_all("li")

    for elem in matches:
        srv, lang = elem.find("span", class_="server").text.replace(" - ", "-").split("-")
        opt = elem.a["href"].replace("#","")
        try:
            url_ = soup.find("div", id="%s" % opt).find("iframe")
            url = url_.get("data-lazy-src", '') or url_.get("data-src", '')
            url = create_soup(url).find("iframe")["src"]
        except:
            continue


        itemlist.append(Item(channel=item.channel, title='%s', url=url, action="play", infoLabels=item.infoLabels,
                             language=IDIOMAS.get(lang, lang)))
    
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
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
        if texto != '':
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

