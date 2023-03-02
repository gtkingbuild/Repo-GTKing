# -*- coding: utf-8 -*-
# -*- Channel UltraPelisHD -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from core.item import Item
from core import scrapertools
from core import servertools
from channelselector import get_thumb
from platformcode import config, logger
from lib.AlfaChannelHelper import DooPlay
from channels import filtertools, autoplay

IDIOMAS = {'la': 'LAT', 'ca': 'CAST', 'su': 'VOSE', 'en': 'VOSE'}
list_language = list(IDIOMAS.values())

list_quality = []

list_servers = [
    'fembed',
    'uqload',
    ]

canonical = {
             'channel': 'ultrapelishd', 
             'host': config.get_setting("current_host", 'ultrapelishd', default=''), 
             'host_alt': ["https://ultrapelishd.net/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
AlfaChannel = DooPlay(host, "/pelicula", canonical=canonical)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Ultimas', url=host + 'genre/estrenos-hd', action='list_all',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Todas', url=host + 'pelicula', action='list_all',
                         thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Netflix', url=host + 'genre/netflix/', action='list_all',
                         thumbnail=get_thumb('movies', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Generos', action='section', url=host,
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + '?s=',
                         thumbnail=get_thumb("search", auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, section="genre")


def findvideos(item):
    logger.info()

    itemlist = list()

    soup, matches = AlfaChannel.get_video_options(item.url)

    for elem in matches:
        lang = elem.find("span", class_="title").text[:2].lower()
        
        data = AlfaChannel.get_data_by_post(elem).json
        
        url = data.get("embed_url", "")
        if not url or "youtube" in url:
            continue
        
        itemlist.append(Item(channel=item.channel, title="%s", action="play", url=url,
                             language=IDIOMAS.get(lang, "LAT"), infoLabels=item.infoLabels))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    if item.contentType != "episode":
        if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != "findvideos":
            itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]",
                                 url=item.url, action="add_pelicula_to_library", extra="findvideos",
                                 contentTitle=item.contentTitle))

    return itemlist


def search(item, texto):
    logger.info()
    
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto

        if texto != '':
            return AlfaChannel.search_results(item, postprocess=get_lang)
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
        if categoria in ['peliculas', 'latino']:
            item.url = host + 'genre/estrenos-hd'
        elif categoria == 'infantiles':
            item.url = host + 'genre/infantil/'
        elif categoria == 'terror':
            item.url = host + 'genre/terror/'
        itemlist = list_all(item)
        if itemlist[-1].title == 'Siguiente >>':
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


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
