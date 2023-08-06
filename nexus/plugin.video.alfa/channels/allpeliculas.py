# -*- coding: utf-8 -*-
# -*- Channel AllPeliculas -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import sys
from core.item import Item
from core import httptools
from core import servertools
from core import scrapertools
from core import tmdb
from platformcode import logger, config
from channelselector import get_thumb
from bs4 import BeautifulSoup
from channels import filtertools
from modules import autoplay
import datetime


list_language = ["LAT"]

list_quality = []
list_servers = ["streampe", "fembed", "jawcloud"]

canonical = {
             'channel': 'allpeliculas', 
             'host': config.get_setting("current_host", 'allpeliculas', default=''), 
             'host_alt': ["https://allpeliculas.se/"], 
             'host_black_list': ["https://allpeliculas.ac/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

forced_proxy_opt = 'ProxyDirect'
this_year = datetime.date.today().year


def create_soup(url, referer=None, unescape=False, forced_proxy_opt=None):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, forced_proxy_opt=forced_proxy_opt, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)

    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Estrenos", url=host + "year_pelicula/%s/" % this_year,
                         action="list_all", thumbnail=get_thumb("premieres", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Todas", url=host + "peliculas", action="list_all",
                         thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", url=host + "peliculas", action="section",
                         thumbnail=get_thumb("all", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", url=host+ "?s=",
                         action="search", thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find("ul", class_="cc-list")

    for elem in matches.find_all("article"):
        url = elem.find("a", class_="btn")["href"]

        full_title = elem.h2.text
        if "netflix" in full_title.lower():
            continue
        try:
            title, year = scrapertools.find_single_match(full_title, "(.*) \((\d{4})\)")
        except:
            title = full_title
            year = "-"
        thumb = elem.img["src"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos", thumbnail=thumb,
                             contentTitle=title, infoLabels={"year": year}, contentType='movie'))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    # Pagination
    try:
        next_page = soup.find("a", class_="next")["href"]
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def section(item):
    logger.info()

    itemlist = list()
    matches = create_soup(host).find_all("li", class_="inline-flex")

    for elem in matches:
        title = elem.a.text
        url = elem.a["href"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url, forced_proxy_opt=forced_proxy_opt)
    matches = soup.find("div", class_="players").find_all("iframe")

    for elem in matches:
        url = elem["data-src"]
        itemlist.append(Item(channel=item.channel, title="%s", url=url, action="play",
                        language="LAT", infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist

def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
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
    itemlist = []
    item = Item()
    try:
        if categoria in ['peliculas','latino']:
            item.url = host + "year_pelicula/%s/" % this_year
            itemlist = list_all(item)

            if itemlist[-1].action == "list_all":
                itemlist.pop()
    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []
    
    return itemlist
