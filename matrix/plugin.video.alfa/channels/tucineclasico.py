# -*- coding: utf-8 -*-
# -*- Channel TuCineClasico -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core.item import Item
from core import servertools
from core import scrapertools
from channelselector import get_thumb
from platformcode import config, logger
from lib.AlfaChannelHelper import DooPlay
from channels import filtertools, autoplay


IDIOMAS = {'es': 'CAST', 'en': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['supervideo']

canonical = {
             'channel': 'tucineclasico', 
             'host': config.get_setting("current_host", 'tucineclasico', default=''), 
             'host_alt': ["https://online.tucineclasico.es/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = DooPlay(host, movie_path="peliculas/", canonical=canonical)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Todas", url=host+'peliculas', action="list_all",
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host,
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Años", action="section", url=host,
                        thumbnail=get_thumb('year', auto=True)))
                        
    itemlist.append(Item(channel=item.channel, title="Alfabético", action="alfabetico", url=host,
                        thumbnail=get_thumb('alphabet', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...",  url=host + '?s=',  action="search",
                         thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item)


def list_all_json(item):
    logger.info()

    return AlfaChannel.list_all_json(item)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, section="genres")
    elif item.title == "Años":
        return AlfaChannel.section(item, section="year")


def alfabetico(item):
    logger.info()
    
    itemlist = []
    url = 'https://online.tucineclasico.es/wp-json/dooplay/glossary/?term=%s&nonce=6f7425652a&type=all'

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        
        itemlist.append(item.clone(action="list_all_json", title=letra, url=url % letra.lower()))
    
    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup, matches = AlfaChannel.get_video_options(item.url)

    for elem in matches:
        if elem["data-nume"] == "trailer":
            continue
        lang = elem.find("span", class_="flag").img["src"]
        lang = scrapertools.find_single_match(lang, "/flags/([^.]+).")
        
        data = AlfaChannel.get_data_by_post(elem).json
        url = data.get("embed_url", "")
        if not url or "youtube" in url or not 'http' in url:
            continue

        itemlist.append(Item(channel=item.channel, title='%s', action='play', url=url,
                            language=IDIOMAS.get(lang, "VOSE"), infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def search_results(item):

    return AlfaChannel.search_results(item, postprocess=get_lang)


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.first = 0
        if texto != '':
            return search_results(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def get_lang(*args):

    langs = list()
    try:
        lang_list = args[1].find_all("span", class_="flag")
        for lang in lang_list:
            lang = scrapertools.find_single_match(lang["style"], r'/flags/(.*?).png\)')
            if not lang in langs:
                langs.append(lang)
    except:
        langs = ""

    args[2].language = langs
    
    return args[2]
