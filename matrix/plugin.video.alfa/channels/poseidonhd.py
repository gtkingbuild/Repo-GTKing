# -*- coding: utf-8 -*-
# -*- Channel PoseidonHD -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import traceback

from core.item import Item
from core import servertools
from core import scrapertools
from channelselector import get_thumb
from platformcode import config, logger
from lib.AlfaChannelHelper import ToroFilm, ToroPdon
from channels import filtertools, autoplay


IDIOMAS = {'mx': 'Latino', 'dk': 'Latino', 'es': 'Castellano', 'en': 'VOSE', 'gb': 'VOSE', 'de': 'Alemán',
           "Latino": "Latino", "Español": "Castellano", "Subtitulado": "VOSE", "usa": "VOSE", "mexico": "Latino",
           "espana": "Castellano"}

list_language = list(set(IDIOMAS.values()))

list_quality = []

list_servers = [
    'gvideo',
    'fembed'
    ]

canonical = {
             'channel': 'poseidonhd', 
             'host': config.get_setting("current_host", 'poseidonhd', default=''), 
             'host_alt': ["https://tekilaz.co/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'CF_stat': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url_replace = [("/series/", "/serie/")]
AlfaChannel = ToroPdon(host, movie_path="/pelicula", tv_path="/serie", canonical=canonical, url_replace=url_replace)
forced_proxy_opt = 'ProxyCF'


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host+'peliculas/', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host+'series/', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    #itemlist.append(Item(channel=item.channel, title='Por Año', action='section', url=host,
    #                     thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + 'search?q=',
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Todas', url=item.url, action='list_all',
                         thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Estrenos', url=item.url+'estrenos', action='list_all',
                         thumbnail=get_thumb('premieres', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Tendencias Semana', url=item.url+'tendencias/semana', action='list_all',
                         thumbnail=get_thumb('last', auto=True), c_type=item.c_type))

    itemlist.append(Item(channel=item.channel, title='Tendencias Día', url=item.url+'tendencias/dia', action='list_all',
                         thumbnail=get_thumb('last', auto=True), c_type=item.c_type))
    
    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title='Generos', action='section', url=host,
                             thumbnail=get_thumb('genres', auto=True), c_type=item.c_type))
    else:
        itemlist.append(Item(channel=item.channel, title='Nuevos Episodios', action='list_all', url=host+'episodios',
                             thumbnail=get_thumb('new episodes', auto=True), c_type='episodios'))

    return itemlist


def list_all(item):
    logger.info()

    #if item.c_type != "search" and not "?type=" in item.url:
    #    item.url += "?type=%s" % item.c_type
    return AlfaChannel.list_all(item, lim_max=24)


def section(item):
    logger.info()

    if item.title == "Generos":
        return AlfaChannel.section(item, menu_id="1953")[1:]
    else:
        return AlfaChannel.section(item, section="year")


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

    itemlist = list()
    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem", "embed": "mystream"}

    soup, matches = AlfaChannel.get_video_options(item.url)

    for lang, elem in matches:

        #srv = re.sub(r"\s+", "", elem.find("span", class_="server"))
        srv = scrapertools.find_single_match(str(elem), '<span>\d+<!--\s*-->.\s*<!--\s*-->\s*([^<]+)<')
        
        try:
            #url = soup.find("div", id="%s" % opt).find("iframe")["data-src"]
            url = scrapertools.find_single_match(str(elem), 'data-tr="([^"]+)"')
        except:
            continue
        if srv.lower() in ["waaw", "jetload"]:
           continue
        if srv.lower() in servers:
           srv = servers[srv.lower()]

        itemlist.append(Item(channel=item.channel, title=srv, url=url, action="play", infoLabels=item.infoLabels,
                             language=IDIOMAS.get(lang, lang), server=srv))

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist


def play(item):
    logger.info()

    itemlist = list()
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': -1, 
              'CF': False, 'cf_assistant': False, 'canonical': {}}
    
    try:
        #data = AlfaChannel.create_soup(item.url, forced_proxy_opt=forced_proxy_opt, **kwargs).find("input")["value"]
        data = AlfaChannel.create_soup(item.url, forced_proxy_opt=forced_proxy_opt, **kwargs).find("script")
        data = url = scrapertools.find_single_match(str(data), "url\s*=\s*'([^']+)'")
        if not data.startswith('http'):
            base_url = "%sr.php" % host
            post = {"data": data}
            url = AlfaChannel.create_soup(base_url, post=post, forced_proxy_opt=forced_proxy_opt, soup=False, **kwargs).url
            if not url: return itemlist
        
        if "fs.%s" % host.replace("https://", "") in url:
            api_url = "%sr.php" % host.replace("https://", "https://fs.")
            v_id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")
            post = {"h": v_id}
            url = AlfaChannel.create_soup(api_url, post=post, forced_proxy_opt=forced_proxy_opt, soup=False, **kwargs).url
        
        itemlist.append(item.clone(url=url, server=""))
        itemlist = servertools.get_servers_itemlist(itemlist)
    except:
        logger.error(traceback.format_exc())

    return itemlist


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto
        item.c_type = "search"
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
            item.url = host + 'movies'
        elif categoria == 'infantiles':
            item.url = host + 'category/animacion/'
        elif categoria == 'terror':
            item.url = host + 'category/terror/'
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

    langs = list()

    if "/series" in args[2].url:
        args[2].context = filtertools.context(args[3], list_language, list_quality)
    else:
        lang_list = args[1].find("span", class_="lang").find_all("img")
        try:
            for lang in lang_list:
                flag = scrapertools.find_single_match(lang["src"], '/flag-([^\.]+)\.')
                langs.append(IDIOMAS.get(flag.lower(), "VOSE"))
        except:
           pass

        args[2].language = langs

    return args[2]

