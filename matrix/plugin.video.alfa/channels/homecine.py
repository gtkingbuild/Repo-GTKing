# -*- coding: utf-8 -*-
# -*- Channel HomeCine -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from channels import autoplay
from channels import filtertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from lib.AlfaChannelHelper import PsyPlay
from channelselector import get_thumb

IDIOMAS = {'Latino': 'LAT', 'Castellano': 'CAST', 'Subtitulado': 'VOSE', 'Ingles': 'VO'}

list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['cinemaupload', 'fastream']

canonical = {
             'channel': 'homecine', 
             'host': config.get_setting("current_host", 'homecine', default=''), 
             'host_alt': ["https://homecine.tv/"], 
             'host_black_list': [], 
             'pattern': '<div\s*class="header-logo">[^>]*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = PsyPlay(host, tv_path="/series", canonical=canonical)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel,title="Películas",
                         action="list_all",
                         thumbnail=get_thumb('movies', auto=True),
                         url='%s%s' % (host, 'peliculas/')
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         title="Series",
                         action="list_all",
                         thumbnail=get_thumb('tvshows', auto=True),
                         url='%s%s'% (host, 'series/')
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         title="Documentales",
                         action="list_all",
                         thumbnail=get_thumb('documentaries', auto=True),
                         url='%s%s' % (host, 'genre/documentales/')
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         title="Generos",
                         action="seccion",
                         thumbnail=get_thumb('genres', auto=True),
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         title="Buscar",
                         action="search",
                         url=host+'?s=',
                         thumbnail=get_thumb('search', auto=True)
                         )
                    )

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item)


def seccion(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, menu_id="20")


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item)


def episodesxseason(item):
    logger.info()

    itemlist = AlfaChannel.episodes(item)

    for item in itemlist:
        if not item.url.startswith(host):
            item.url = host + item.url
    return itemlist


def episodios(item):
    logger.info()

    itemlist = list()
    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup, matches = AlfaChannel.get_video_options(item.url)

    for elem in matches:
        lang = elem.a.string.split(" - ")[1]
        opt = elem.a["href"][1:]
        url = soup.find(id=opt).iframe["src"]

        itemlist.append(Item(channel=item.channel,
                             url=url,
                             title= '%s',
                             action='play',
                             language=IDIOMAS.get(lang, "LAT"),
                             infoLabels=item.infoLabels
                             )
                        )

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if item.contentType != "episode":

        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
            itemlist.append(Item(channel=item.channel,
                                 title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                                 url=item.url,
                                 action="add_pelicula_to_library",
                                 extra="findvideos",
                                 contentTitle=item.contentTitle,
                                 setMimeType='application/vnd.apple.mpegurl'
                                 )
                            )

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    try:
        return list_all(item)
    except:
        import sys
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
            item.url = host + 'genre/animacion/'
        elif categoria == 'terror':
            item.url = host + 'genre/terror/'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>>':
            itemlist.pop()
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


