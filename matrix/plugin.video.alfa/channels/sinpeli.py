# -*- coding: utf-8 -*-
# -*- Channel SinPeli -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import base64

from channels import filtertools
from bs4 import BeautifulSoup
from core import servertools, scrapertools
from core.item import Item
from channels import autoplay
from lib.AlfaChannelHelper import ToroPlay
from platformcode import config, logger
from channelselector import get_thumb

IDIOMAS = {'la': 'LAT', 'ca': 'CAST', 'su': 'VOSE'}
list_idiomas = list(set(IDIOMAS.values()))

list_servers = ['okru', 'yourupload', 'mega', 'doodstream', 'fembed']
list_quality = []

canonical = {
             'channel': 'sinpeli', 
             'host': config.get_setting("current_host", 'sinpeli', default=''), 
             'host_alt': ["https://www.sinpeli.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = ToroPlay(host, canonical=canonical)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel,
                         action="list_all",
                         thumbnail=get_thumb("All", auto=True),
                         title="Todas",
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="section",
                         thumbnail=get_thumb("language", auto=True),
                         title="Idiomas",
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="section",
                         thumbnail=get_thumb("quality", auto=True),
                         title="Calidad",
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="section",
                         thumbnail=get_thumb("genres", auto=True),
                         title="Generos",
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="search",
                         thumbnail=get_thumb("search", auto=True),
                         url=host + "?s=",
                         title="Buscar..."
                         )
                    )

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, postprocess=get_languages)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, menu_id="351")
    elif item.title == "Idiomas":
        return AlfaChannel.section(item, menu_id="415")
    else:
        return AlfaChannel.section(item, menu_id="421")


def findvideos(item):
    logger.info()

    itemlist = list()
    patron_php = "<iframe\s*src='([^']+)'"
    patron_link = "\('([^']+)'"
    lang = "la"
    infoLabels = item.infoLabels

    soup, matches = AlfaChannel.get_video_options(item.url)

    for btn in matches:
        b_data = btn["data-player"]
        b_data = base64.b64decode(b_data).decode('utf-8')
        if not b_data: 
            continue
        if scrapertools.find_single_match(b_data, patron_php):
            b_data = scrapertools.find_single_match(b_data, patron_php)
            
            if 'links.cuevana3' in b_data:
                soup, matches = AlfaChannel.get_video_options(b_data)

                if not matches:
                    try:
                        matches = soup.find("div", class_="REactiv").find_all("li")
                    except:
                        continue

                for link in matches:
                    link_url = link["onclick"]
                    if not scrapertools.find_single_match(link_url, patron_link): 
                        continue
                    b_data = scrapertools.find_single_match(link_url, patron_link)
                    srv = link.span.text.lower()
                    if "trailer" in srv:
                        continue
                    try:
                        lang = link.p.text
                        if 'Espanol' in lang: lang = 'ca'
                        if 'Latino' in lang: lang = 'la'
                        if 'Subtitulado' in lang: lang = 'su'
                    except:
                        lang = "la"
                        
                    itemlist.append(Item(channel=item.channel,
                                         action='play',
                                         infoLabels=infoLabels,
                                         language=IDIOMAS.get(lang.lower(), "LAT"),
                                         server=srv.split('.')[0],
                                         title=srv.split('.')[0].capitalize(),
                                         url=b_data
                                        )
                                    )
            else:
                srv = btn.span.text.lower()
                if "trailer" in srv.lower():
                    continue
                try:
                    lang = btn.span.next_sibling.text[:2]
                    if 'Espanol' in lang: lang = 'ca'
                    if 'Latino' in lang: lang = 'la'
                    if 'Subtitulado' in lang: lang = 'su'
                except:
                    lang = "la"

                itemlist.append(Item(channel=item.channel,
                                     action='play',
                                     infoLabels=infoLabels,
                                     language=IDIOMAS.get(lang.lower(), "LAT"),
                                     server='',
                                     title=srv.capitalize(),
                                     url=b_data
                                    )
                                )

    itemlist = sorted(itemlist, key=lambda i: i.server)
    itemlist = servertools.get_servers_itemlist(itemlist)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and (
            not item.videolibrary or item.extra != 'findvideos'):
        itemlist.append(Item(action="add_pelicula_to_library",
                             contentTitle=item.contentTitle,
                             channel=item.channel,
                             extra="findvideos",
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url
                            )
                        )

    return itemlist


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        if texto != '':
            item.url += texto
            item.search = True
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
            item.url = host
        elif categoria == 'latino':
            item.url = host + "idioma/latino/"
        elif categoria == 'castellano':
            item.url = host + "idioma/castellano"
        elif categoria == 'infantiles':
            item.url = host + 'animacion'
        elif categoria == 'terror':
            item.url = host + 'terror'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def get_languages(*args):
    logger.info()

    try:
        lang = args[1].find("span", class_="languages").text.strip()[:2]
    except:
        lang = "la"

    args[2].language = IDIOMAS.get(lang.lower(), "la")

    return args[2]