# -*- coding: utf-8 -*-
# -*- Channel BlogHorror -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import os
import re
import traceback

from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger, subtitletools
from channelselector import get_thumb

canonical = {
             'channel': 'bloghorror', 
             'host': config.get_setting("current_host", 'bloghorror', default=''), 
             'host_alt': ["https://bloghorror.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': 'ProxyCF', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
fanart = host + 'wp-content/uploads/2015/04/bloghorror-2017-x.jpg'


def create_soup(url, referer=None, unescape=False, ignore_response_code=True):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, ignore_response_code=ignore_response_code, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, ignore_response_code=ignore_response_code, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def mainlist(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, fanart=fanart, title="Todas", action="list_all",
                         url=host+'category/terror-2', thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, fanart=fanart, title="Asiaticas", action="list_all",
                         url=host+'category/asiatico1', thumbnail=get_thumb('asiaticas', auto=True)))

    itemlist.append(Item(channel=item.channel, fanart=fanart, title = 'Buscar', action="search", url=host + '?s=', pages=3,
                         thumbnail=get_thumb('search', auto=True)))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)

    matches = soup.find(id="primary").find_all("article")

    for elem in matches:
        cat = elem.find("a", class_="covernews-categories")["alt"]
        if cat in ["View all posts in Las Mejores Peliculas de Terror", "View all posts in Editoriales"]:
            continue
        title_data = elem.find("h3", class_="article-title").text.strip()
        if "(" in title_data:
            title = title_data.replace(")", "").split(" (")
        elif "[" in title_data:
            title = title_data.replace("]", "").split(" [")
        url = elem.find("h3", class_="article-title").a["href"]
        thumb = elem.find("div", class_="data-bg-hover")["data-background"]
        try:
            year = title[1]
        except:
            year = "-"

        if "serie" in url:
            continue

        itemlist.append(Item(channel=item.channel, title=title[0], url=url, contentTitle=title[0], thumbnail=thumb,
                             action="findvideos", infoLabels={"year": year}))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    # Paginacion
    if itemlist:

        try:
            next_page = soup.find("div", class_="navigation").find("a", class_="next")["href"]

            if next_page != '':
                itemlist.append(Item(channel=item.channel, fanart=fanart, action="list_all", title='Siguiente >>>',
                                     url=next_page))
        except:
            pass

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", class_="entry-content-wrap")
    
    quality = scrapertools.find_single_match(soup.text, r"Calidad: ([^\n]+)\n").split("+")
    urls_list = soup.find_all("a", {"data-wpel-link": True, "href": re.compile("magnet|torrent")})
    try:
        sub_url = soup.find("a", {"data-wpel-link": True, "href": re.compile("subdivx")})["href"]
    except:
        sub_url = ""
    qlty_cnt = 0

    for url in urls_list:
        url = url["href"]

        if not sub_url:
            lang = 'VO'
        else:
            lang = 'VOSE'
        try:
            qlty = quality[qlty_cnt]
            qlty_cnt += 1
        except:
            qlty = "SD"


        itemlist.append(Item(channel=item.channel, title="[%s][%s][%s]", url=url, action="play", quality=qlty,
                             language=lang, subtitle=sub_url, infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % (i.server, i.language, i.quality))

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_pelicula_to_library",
                             extra="findvideos",
                             contentTitle=item.contentTitle
                             ))

    return itemlist


def play(item):
    logger.info()
    
    if item.subtitle:
        try:
            sub = subtitletools.get_from_subdivx(item.subtitle)
            return [item.clone(subtitle=sub)]
        except:
            logger.error('ERROR en Subtítulos: %s' % traceback.format_exc())
            return [item]
    else:
        return [item]


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
        import sys

        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria):
    logger.info()
    
    itemlist = []
    item = Item()
    
    try:
        if categoria in ['peliculas', 'terror', 'torrent']:
            item.url = host
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
