# -*- coding: utf-8 -*-
# -*- Channel DoramedPlay -*-
# -*- BASED ON: Channel DramasJC -*-
# -*- Created for Alfa-addon -*-

import requests
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
from lib.AlfaChannelHelper import DooPlay
from channels import filtertools

IDIOMAS = {'VOSE': 'VOSE', 'LAT': 'LAT'}
list_language = list(IDIOMAS.values())
list_quality = list()
list_servers = ['okru', 'mailru', 'openload']

canonical = {
             'channel': 'doramedplay', 
             'host': config.get_setting("current_host", 'doramedplay', default=''), 
             'host_alt': ["https://doramedplay.com/"], 
             'host_black_list': [], 
             'pattern': '<link\s*rel="stylesheet"\s*id="[^"]*"\s*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = DooPlay(host, tv_path="tvshows", canonical=canonical)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()
    itemlist.append(Item(channel=item.channel, title="Doramas", action="list_all", url=host+'tvshows/',
                         type="tvshows", thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", url=host+'movies/',
                         type='movies', thumbnail=get_thumb('movies', auto=True)))
    
    #itemlist.append(Item(channel=item.channel, title="Generos", action="section",
    #                     url=host, thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host+'?s=',
                               thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, postprocess=set_plot)

def section(item):

    if item.title == "Generos":
        return AlfaChannel.section(item, section="genres")


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item)


def episodios(item):
    logger.info()
    
    itemlist = []
    
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    return AlfaChannel.episodes(item)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup, matches = AlfaChannel.get_video_options(item.url)

    for elem in matches:
        data = AlfaChannel.get_data_by_post(elem).json
        itemlist.append(Item(channel=item.channel, title='%s', url=data['embed_url'], action='play', 
                             infoLabels=item.infoLabels, contentType='episode'))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))


    return itemlist


def search(item, texto):
    logger.info()
    
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    try:
        return AlfaChannel.search_results(item, next_pag=True)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def search_more(item):
    logger.info()

    try:
        return AlfaChannel.search_results(item, next_pag=True)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def set_plot(*args):

    plot = args[1].find("div", "texto").string
    args[2].plot = plot

    return args[2]
