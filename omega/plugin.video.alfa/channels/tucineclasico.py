# -*- coding: utf-8 -*-
# -*- Channel TuCineClasico -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel, DooPlay
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'tucineclasico', 
             'host': config.get_setting("current_host", 'tucineclasico', default=''), 
             'host_alt': ["https://online.tucineclasico.es/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/serie'
language = ['LAT']
url_replace = []

AlfaChannel_class = DooPlay(host, canonical=canonical, channel=canonical['channel'], language=language, idiomas=IDIOMAS, 
                            list_language=list_language, list_servers=list_servers, url_replace=url_replace, debug=debug)
finds = AlfaChannel_class.finds
finds['controls']['add_video_to_videolibrary'] = True

AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Todas", url=host+'peliculas', action="list_all",
                         thumbnail=get_thumb('all', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Género[/COLOR]", action="section", url=host,
                         thumbnail=get_thumb('genres', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Año[/COLOR]", action="section", url=host,
                        thumbnail=get_thumb('year', auto=True), c_type='peliculas'))
                        
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por [A-Z][/COLOR]", action="alfabetico", url=host,
                        thumbnail=get_thumb('alphabet', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title="Buscar...",  url=host,  action="search",
                         thumbnail=get_thumb('search', auto=True), c_type='search'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if "Género" in item.title:
        findS['categories']['find'][0]['id'][0] = 'menu-item-97'
    elif "Año" in item.title:
        findS['categories'] = dict([('find', [{'tag': ['ul'], 'class': ['releases']}]), 
                                    ('find_all', [{'tag': ['li']}])])

    return AlfaChannel.section(item, finds=findS, **kwargs)


def alfabetico(item):
    logger.info()

    itemlist = []
    url = 'https://online.tucineclasico.es/wp-json/dooplay/glossary/?term=%s&nonce=6f7425652a&type=all'

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

        itemlist.append(item.clone(action="list_all", title=letra, url=url % letra.lower(), json=True))

    return itemlist


def list_all(item):
    logger.info()

    findS = finds.copy()

    findS['year'] = dict([('find', [{'tag': ['span']}]), 
                          ('get_text', [{'@TEXT': '(\d{4})'}])])

    if item.c_type == 'search':
        findS['find'] = findS.get('search', findS['find'])
        findS['controls']['get_lang'] = True
        return AlfaChannel.list_all(item, matches_post=AlfaChannel_class.list_all_matches, finds=findS, **kwargs)

    if item.json:
        findS['find'] = dict([('find', [{'tag': ['body']}]), 
                              ('get_text', [{'@TEXT': '(.*?)$'}])])

    return AlfaChannel.list_all(item, matches_post=AlfaChannel_class.list_all_matches, finds=findS, **kwargs)


def findvideos(item):
    logger.info()

    findS = finds.copy()

    findS['get_language'] = {'find_all': [{'tag': ['img'], '@ARG': 'src'}]}
    findS['controls']['get_lang'] = True

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=AlfaChannel_class.findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, finds=findS, **kwargs)


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + '?s=' + texto
        item.first = 0

        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
