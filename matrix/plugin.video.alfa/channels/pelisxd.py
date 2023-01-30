# -*- coding: utf-8 -*-
# -*- Channel PelisXD -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core.item import Item
from core import scrapertools
from channelselector import get_thumb
from platformcode import config, logger
from lib.AlfaChannelHelper import ToroFilm
from channels import filtertools, autoplay

IDIOMAS = {'la': 'Latino', 'es': 'Castellano', 'us': 'VOSE'}
list_language = list(set(IDIOMAS.values()))

list_quality = []

list_servers = [
    'gvideo',
    'fembed'
    ]

canonical = {
             'channel': 'pelisxd', 
             'host': config.get_setting("current_host", 'pelisxd', default=''), 
             'host_alt': ["https://www.pelisxd.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': 'ProxyCF', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = ToroFilm(host, tv_path="/serie", canonical=canonical)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu',
                         thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True),  extra='movie'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.title != "Peliculas":
        c_type = "series-y-novelas"
    else:
        c_type = item.title.lower()

    itemlist.append(Item(channel=item.channel, title='Ultimas', url=host + c_type, action='list_all',
                         thumbnail=get_thumb('all', auto=True), c_type=c_type))

    itemlist.append(
        Item(channel=item.channel, title='Generos', action='section', thumbnail=get_thumb('genres', auto=True),
             url=host, c_type=c_type))

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, postprocess=get_language_and_set_filter)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, menu_id="354", postprocess=set_type)


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item)


def episodesxseason(item):
    logger.info()

    return AlfaChannel.episodes(item)


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def findvideos(item):
    logger.info()
    servers = {"femax20": "fembed", "embed": "mystream", "dood": "doodstream"}
    itemlist = list()

    soup, matches = AlfaChannel.get_video_options(item.url)

    for elem in matches:

        srv, lang = re.sub(r"\s+", "", elem.find("span", class_="server").text).split("-")
        opt = elem.a["href"][1:]
        try:
            url = soup.find("div", id="%s" % opt).find("iframe")["data-src"]
        except:
            continue
        if srv.lower() in servers:
            srv = servers.get(srv.lower(), "directo")
        itemlist.append(Item(channel=item.channel, title=srv, url=url, action="play", infoLabels=item.infoLabels,
                             language=IDIOMAS.get(lang, lang), server=srv.lower()))

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
        if categoria in ['peliculas']:
            item.url = host + 'peliculas'
        elif categoria == 'infantiles':
            item.url = host + 'animacion/?type=movies'
        elif categoria == 'terror':
            item.url = host + 'terror/?type=movies'
        item.type = "movies"
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def get_language_and_set_filter(*args):
    logger.info()

    language = list()
    lang = ""

    if "/serie" in args[2].url:
        args[2].context = filtertools.context(args[3], list_language, list_quality)
    else:
        lang_list = args[1].find_all("span", class_="lang")
        for lang in lang_list:
            lang = scrapertools.find_single_match(lang.img.get("data-lazy-src", "") or lang.img.get("src", ""), r'/\d{02}/([^.]+).png')
            if lang and lang not in language:
                language.append(IDIOMAS[lang])

        args[2].language = lang

    return args[2]


def set_type(*args):
    if args[2].c_type == "peliculas":
        args[2].url += "?type=movies"
    else:
        args[2].url += "?type=series"

    return args[2]
