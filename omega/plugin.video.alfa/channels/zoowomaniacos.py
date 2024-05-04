# -*- coding: utf-8 -*-
# -*- Channel Zoowomaniacos -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

if not PY3:
    from lib import alfaresolver
else:
    from lib import alfaresolver_py3 as alfaresolver

IDIOMAS = AlfaChannelHelper.IDIOMAS
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'zoowomaniacos', 
             'host': config.get_setting("current_host", 'zoowomaniacos', default=''), 
             'host_alt': ["https://zoowomaniacos.org/"], 
             'host_black_list': [], 
             'status': 'SIN CANONICAL NI DOMINIO',
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt,
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/serie'
language = []
url_replace = []

finds = {'findvideos': dict([('find', [{'tagOR': ['div'], 'id': ['playeroptions']}, 
                                       {'tag': ['ul'], 'class': ['options']}]), 
                             ('find_all', [{'tag': 'li'}])]), 
         'get_language_rgx': '(?:flags\/|-)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 
                      'custom_pagination': True, 'cnt_tot': 20}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    
    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title='Ultimas', start=0, action='list_all', 
                         thumbnail=get_thumb('last', auto=True)))

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Género[/COLOR]', action='section',
                         thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Año[/COLOR]', action='section',
                         thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por País[/COLOR]', action='section',
                         thumbnail=get_thumb('country', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    itemlist = list()

    if "Género" in item.title:
        _filter = "genres"
    elif "País" in item.title:
        _filter = "countries"
    else:
        _filter = "years"

    matches = alfaresolver.get_data_zw(host, item, section=True).get(_filter, [])

    for elem in matches:
        title = elem.get("label", '')
        new_item = item.clone(title=title, action="list_all", start=0)

        if "Género" in item.title:
            new_item.genre = title
        elif "País" in item.title:
            new_item.country = title
        else:
            new_item.year = title

        itemlist.append(new_item)
        
    if _filter == "years":
        itemlist.reverse()

    return itemlist


def list_all(item):
    logger.info()

    kwargs['matches_post_json_force'] = True

    item.matches = alfaresolver.get_data_zw(host, item)
    
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    item.contentType = 'movie'

    for elem in matches_int.get("matches", {}):
        elem_json = {}

        elem_json['title'] = elem.get("a2", "").split("-")[0].strip()
        elem_json['url'] = item.url or host
        lang = scrapertools.find_single_match(elem.get("a8", ""), findS['get_language_rgx']) \
                            if findS['controls']['get_lang'] else ''
        if lang.lower() in ["ar", "mx", "pe", "cl", "co"]: lang = "la"
        elem_json['language'] = IDIOMAS.get(lang, '*%s' % lang)
        elem_json['quality'] = '*'
        elem_json['info'] = {'v_id': elem.get("a1", "0")}
        elem_json['plot'] = elem.get("a100", "")
        elem_json['thumbnail'] = "%swp/wp-content/uploads/%s" % (host, elem.get("a8", ""))
        if ('tmdb' in elem_json['thumbnail'] or 'imdb' in elem_json['thumbnail']) and '=http' in elem_json['thumbnail']:
            elem_json['thumbnail'] = scrapertools.find_single_match(AlfaChannel.do_unquote(elem_json['thumbnail']), '=(.*?)[&|$]')
        elem_json['year'] = elem.get("a4", "-")

        matches.append(elem_json.copy())
    
    if matches_int.get("pagination", False):
        item.start += len(matches)
    else:
        item.start = 20

    return matches


def findvideos(item):
    logger.info()

    base_url = "https://proyectox.yoyatengoabuela.com/testplayer.php?id=%s" % item.info.get('v_id', '0')
    
    return AlfaChannel.get_video_options(item, base_url, matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})
    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem", "embed": "mystream"}

    for elem in matches_int[1:]:
        elem_json = {}

        elem_json['server'] = elem.get('cyberlocker', '')
        elem_json['url'] = soup.find("div", id=elem.a.get("href", "")[1:]).iframe.get("src", "")
        lang = scrapertools.find_single_match(elem.img.get("src", ''), findS['get_language_rgx']) \
                            if findS['controls']['get_lang'] else ''
        if lang.lower() in ["ar", "mx", "pe", "cl", "co"]: lang = "la"
        elem_json['language'] = IDIOMAS.get(lang, '*%s' % lang)
        elem_json['quality'] = '*%s' % elem.get('quality', '')
        elem_json['title'] = '%s'

        if not elem_json['url']: continue

        if elem_json['server'].lower() in ["waaw", "jetload"]: continue
        if elem_json['server'].lower() in servers:
           elem_json['server'] = servers[elem_json['server'].lower()]

        matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    try:
        texto = texto.replace(" ", "+")
        item.search = item.url + texto
        item.start = 0

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
