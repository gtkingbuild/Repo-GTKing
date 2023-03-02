# -*- coding: utf-8 -*-
# -*- Channel Zoowomaniacos -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core import tmdb
from core.item import Item
from core import servertools
from core import scrapertools
if not PY3:
    from lib import alfaresolver
else:
    from lib import alfaresolver_py3 as alfaresolver
from channelselector import get_thumb
from platformcode import config, logger
from lib.AlfaChannelHelper import DooPlay
from channels import filtertools, autoplay

IDIOMAS = {'es': 'CAST', 'la': 'LAT'}
list_language = list(set(IDIOMAS.values()))

list_quality = []

list_servers = [
    'okru'
    ]

canonical = {
             'channel': 'zoowomaniacos', 
             'host': config.get_setting("current_host", 'zoowomaniacos', default=''), 
             'host_alt': ["https://zoowomaniacos.org/"], 
             'host_black_list': [], 
             'status': 'SIN CANONICAL NI DOMINIO',
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = DooPlay(host, canonical=canonical)


def mainlist(item):
    logger.info()
    
    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title='Ultimas', start=0, action='list_all', thumbnail=get_thumb('last', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Generos', action='section',
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Por Año', action='section',
                         thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Por País', action='section',
                    thumbnail=get_thumb('country', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    if item.title == "Generos":
        _filter = "genres"
    elif item.title == "Por País":
        _filter = "countries"
    else:
        _filter = "years"

    matches = alfaresolver.get_data_zw(host, item, section=True).get(_filter, [])

    for elem in matches:
        title = elem["label"]
        new_item = Item(channel=item.channel, title=title, action="list_all", start=0)

        if item.title == "Generos":
            new_item.genres = title
        elif item.title == "Por País":
            new_item.country = title
        else:
            new_item.year = title

        itemlist.append(new_item)
        
    if _filter == "years":
        itemlist.reverse()

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    matches = alfaresolver.get_data_zw(host, item)

    for elem in matches.get("matches", []):

        title = elem.get("a2", "").split("-")[0].strip()
        v_id = elem.get("a1", "0")
        plot = elem.get("a100", "")
        thumb = "%swp/wp-content/uploads/%s" % (host, elem.get("a8", ""))

        new_item = Item(channel=item.channel, title=title, v_id=v_id, thumbnail=thumb, plot=plot,
                        infoLabels={"year": elem.get("a4", "-")})

        new_item.contentTitle = title
        new_item.contentType = 'movie'
        new_item.action = "findvideos"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    if matches.get("pagination", False):
        url_next_page = item.url
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page,
                             start=item.start + 20, search=item.search, genre=item.genre, action='list_all'))

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    base_url = "https://proyectox.yoyatengoabuela.com/testplayer.php?id=%s" % item.v_id
    
    soup, matches = AlfaChannel.get_video_options(base_url)

    for elem in matches[1:]:

        lang = scrapertools.find_single_match(elem.img["src"], "flags/(\w+).png")
        if lang.lower() in ["ar", "mx", "pe", "cl", "co"]:
            lang = "la"

        url = soup.find("div", id=elem.a["href"][1:]).iframe["src"]
        
        itemlist.append(Item(channel=item.channel, title='%s', url=url, action="play", infoLabels=item.infoLabels,
                             language=IDIOMAS.get(lang, "VO")))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.servers.capitalize())

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
        item.search = item.url + texto
        item.start = 0
        if texto != '':
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
