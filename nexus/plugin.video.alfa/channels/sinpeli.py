# -*- coding: utf-8 -*-
# -*- Channel SinPeli -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'sinpeli', 
             'host': config.get_setting("current_host", 'sinpeli', default=''), 
             'host_alt': ["https://www.sinpeli.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/tv'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['MovieList']}]), 
                       ('find_all', [{'tag': ['article',], 'class': re.compile("TPost C")}])]),
         'categories': {}, 
         'search': {}, 
         'get_language': {'find_all': [{'tag': ['span'], 'class': ['languages']}]}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': {'find': [{'tag': ['a'], 'class': ['last'], '@ARG': 'href', '@TEXT': '(\d+)'}]}, 
         'year': dict([('find', [{'tag': ['h3']}]), 
                       ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '\((\d+)\)'}])]), 
         'season_episode': {}, 
         'seasons': {}, 
         'season_num': {}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': dict([('find', [{'tag': ['div'], 'class': ['Description']}, {'tag': ['p']}]), 
                       ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'findvideos': dict([('find', [{'tag': ['ul'], 'class': ['TPlayerNv']}]), 
                             ('find_all', [{'tag': ['li']}])]), 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 14, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel,
                         action="list_all",
                         thumbnail=get_thumb("All", auto=True),
                         title="Todas",
                         c_type='peliculas', 
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="section",
                         thumbnail=get_thumb("language", auto=True),
                         title=" - [COLOR paleturquoise]Idiomas[/COLOR]",
                         c_type='peliculas', 
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="section",
                         thumbnail=get_thumb("quality", auto=True),
                         title=" - [COLOR paleturquoise]Calidad[/COLOR]",
                         c_type='peliculas', 
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="section",
                         thumbnail=get_thumb("genres", auto=True),
                         title=" - [COLOR paleturquoise]Géneros[/COLOR]",
                         c_type='peliculas', 
                         url=host
                         )
                    )

    itemlist.append(Item(channel=item.channel,
                         action="search",
                         thumbnail=get_thumb("search", auto=True),
                         url=host,
                         c_type='search', 
                         title="Buscar..."
                         )
                    )

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    if "Géneros" in item.title: menu_id="351"
    elif "Idiomas" in item.title: menu_id="415"
    else: menu_id="421"
    
    findS = finds.copy()

    findS['categories'] = dict([('find', [{'tag': ['li'], 'id': ['menu-item-%s' % menu_id]}]), 
                                ('find_all', [{'tag': ['li']}])])

    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.extra == 'alpha':
                if not elem.find("a", class_="MvTbImg"): continue
                elem_json['url'] = elem.find("a", class_="MvTbImg").get("href", "")
                elem_json['title'] = elem.find("td", class_="MvTbTtl").get_text(strip=True)
            else:
                elem_json['url'] = elem.a.get("href", "")
                elem_json['title'] = elem.a.h3.get_text(strip=True)
            elem_json['thumbnail'] = elem.find("img")
            elem_json['thumbnail'] = elem_json['thumbnail']["data-src"] if elem_json['thumbnail']\
                                               .has_attr("data-src") else elem_json['thumbnail']["src"]
            if elem.find('span', class_="Qlty"): elem_json['quality'] = '*%s' \
                                                 % elem.find('span', class_="Qlty").get_text(strip=True).replace('Desconocido', '')
            elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))
            AlfaChannel.get_language_and_set_filter(elem, elem_json)
            elem_json['plot'] = AlfaChannel.parse_finds_dict(elem, findS.get('plot', {}), c_type=item.c_type)
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    import base64

    matches = []
    findS = AHkwargs.get('finds', finds)

    servers = {"femax20": "fembed", "embed": "mystream", "dood": "doodstream", "ok": "okru"}
    patron_php = "<iframe\s*src='([^']+)'"
    patron_link = "\('([^']+)'"

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['server'] = ''
            elem_json['url'] = elem.get("data-player", '')
            elem_json['url'] = base64.b64decode(elem_json['url']).decode('utf-8')
            if not elem_json['url']: 
                continue
            if scrapertools.find_single_match(elem_json['url'], patron_php):
                elem_json['url'] = scrapertools.find_single_match(elem_json['url'], patron_php)

            if 'links.cuevana3' in elem_json['url']:
                elem_json['url'] = re.sub("amp;|#038;", "", elem_json['url'])

                links = AlfaChannel.create_soup( elem_json['url'], referer=item.url).find("div", class_="REactiv").find_all("li")
                
                for link in links:
                    elem_json = {}
                    #logger.error(link)

                    elem_json['url'] = link.get("onclick", '')
                    if not scrapertools.find_single_match(elem_json['url'], patron_link): 
                        continue
                    elem_json['url'] = scrapertools.find_single_match(elem_json['url'], patron_link)
                    elem_json['url'] = re.sub("amp;|#038;", "", elem_json['url'])

                    elem_json['server'] = link.span.get_text(strip=True).lower().split('.')[0]
                    if "trailer" in elem_json['server']:
                        continue
                    if elem_json['server'].lower() in servers: elem_json['server'] = servers[elem_json['server'].lower()]
                    if elem_json['server'].lower() in ["waaw", "jetload", "player"]: continue
                    if 'mega.' in elem_json['url']: elem_json['url'] = elem_json['url'].replace("/embed/", "/file/")

                    elem_json['title'] = '%s'

                    elem_json['language'] = item.language

                    if not elem_json['url']: continue

                    matches.append(elem_json.copy())

            else:
                elem_json['url'] = re.sub("amp;|#038;", "", elem_json['url'])

                elem_json['server'] = elem.span.get_text(strip=True).lower().split('.')[0]
                if elem_json['server'].lower() in servers: elem_json['server'] = servers[elem_json['server'].lower()]
                if elem_json['server'].lower() in ["waaw", "jetload", "player"]: continue
                if "trailer" in elem_json['server']:
                    continue

                elem_json['title'] = '%s'

                elem_json['language'] = item.language

                if not elem_json['url']: continue

                matches.append(elem_json.copy())
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

    return matches, langs


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    try:
        texto = texto.replace(" ", "+")
        if texto:
            item.url += "?s=" + texto
            item.c_type = 'peliculas'
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

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
        
        item.c_type = "movies"
        itemlist = list_all(item)
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
