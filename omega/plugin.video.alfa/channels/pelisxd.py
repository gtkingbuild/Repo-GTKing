# -*- coding: utf-8 -*-
# -*- Channel PelisXD -*-
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

IDIOMAS = AlfaChannelHelper.IDIOMAS_T
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'pelisxd', 
             'host': config.get_setting("current_host", 'pelisxd', default=''), 
             'host_alt': ["https://www.pelisxd.com/"], 
             'host_black_list': [], 
             'pattern_proxy': 'span\s*class="server"', 'proxy_url_test': 'pelicula/black-adam/', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/serie'
language = ['LAT']
url_replace = []

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['post-lst']}]), 
                       ('find_all', [{'tag': ['article'], 'class': ['post']}])]),
         'categories': dict([('find', [{'tag': ['li'], 'id': ['menu-item-354']}]), 
                             ('find_all', [{'tag': ['li']}])]), 
         'search': {}, 
         'get_language': {'find': [{'tag': ['span'], 'class': ['lang']}]}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['a'], 'string': re.compile('(?i)siguiente')}]), 
                            ('find_previous', [{'tag': ['a'], 'class': ['page-link']}]), 
                            ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'year': {'find': [{'tag': ['span'], 'class': ['year']}], 'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['li'], 'class': ['sel-temp']}]}, 
         'season_num': {'find': [{'tag': ['a'], '@ARG': 'data-season'}]}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['article'], 'class': ['post dfx fcl episodes fa-play-circle lg']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['aside'], 'class': ['video-player']}]), 
                             ('find_all', [{'tag': ['div'], 'class': ['video']}])]), 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 16, 
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

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host+'peliculas/', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host+'series-y-novelas/', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True),  c_type='search'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(item.clone(title='Ultimas', action='list_all',
                    thumbnail=get_thumb('all', auto=True)))

    itemlist.append(item.clone(title='Generos', action='section', 
                    thumbnail=get_thumb('genres', auto=True)))

    if item.c_type == 'peliculas':
        itemlist.append(item.clone(title='Alfabético', action='alfabetico', 
                        thumbnail=get_thumb('alphabet', auto=True)))

    return itemlist


def section(item):
    logger.info()

    return AlfaChannel.section(item, postprocess=section_postprocess, **kwargs)


def section_postprocess(elem, new_item, item, **AHkwargs):

    findS = AHkwargs.get('finds', finds)

    if new_item.c_type == "peliculas":
        new_item.url += "?type=movies"
    else:
        new_item.url += "?type=series"

    return new_item


def alfabetico(item):
    logger.info()

    itemlist = []
    item.extra = 'continue'

    for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

        itemlist.append(item.clone(action="list_all", title=letra, url=host + 'letter/%s' % letra))

    return itemlist


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
            elem_json['url'] = elem.a.get("href", "")
            if item.c_type == 'peliculas' and tv_path in elem_json['url']: continue
            if item.c_type == 'series' and movie_path in elem_json['url']: continue
            elem_json['title'] = elem.find('h2', class_="entry-title").get_text(strip=True)
            elem_json['thumbnail'] = elem.find("img")
            elem_json['thumbnail'] = elem_json['thumbnail']["data-lazy-src"] if elem_json['thumbnail']\
                                               .has_attr("data-lazy-src") else elem_json['thumbnail']["src"]
            AlfaChannel.get_language_and_set_filter(elem, elem_json)
            if elem.find('span', class_="Qlty"): elem_json['quality'] = '*%s' % elem.find('span', class_="Qlty").get_text(strip=True)
            elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, matches_post=seasons_matches, **kwargs)


def seasons_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            elem_json['season'] = int(AlfaChannel.parse_finds_dict(elem, findS['season_num']) or '1')
            elem_json['post'] = {
                                 "action": "action_select_season",
                                 "season": elem_json['season'],
                                 "post": elem.a.get("data-post", '')
                                }
            elem_json['url'] = elem.a.get('href', item.url)
            if 'javascript' in elem_json['url']: elem_json['url'] = AlfaChannel.doo_url
            if elem_json['url'].startswith('#'):
                elem_json['url'] = AlfaChannel.urljoin(item.url, elem_json['url'])
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url', ''): continue

        matches.append(elem_json.copy())

    return matches


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.find("h2", class_="entry-title").get_text(strip=True)
            try:
                elem_json['season'] = int(elem.find("span", class_="num-epi").get_text(strip=True).split("x")[0].strip() or item.contentSeason)
                elem_json['episode'] = int(elem.find("span", class_="num-epi").get_text(strip=True).split("x")[1].strip() or 1)
            except:
                elem_json['season'] = item.contentSeason
                elem_json['episode'] = 1
            elem_json['thumbnail'] = elem.img.get('src', '')
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url', ''): continue
 
        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    servers = {"femax20": "fembed", "embed": "mystream", "dood": "doodstream"}
    findS_findvideos = dict([('find', [{'tag': ['aside'], 'class': ['video-options']}]), 
                             ('find_all', [{'tag': ['li']}])])
    server_names = AlfaChannel.parse_finds_dict(AlfaChannel.response.soup, findS_findvideos, c_type=item.c_type)

    for server, elem in zip(server_names, matches_int):
        elem_json = {}
        #logger.error(elem)

        try:
            if server.find('span', class_='server'):
                server_lang = server.find('span', class_='server').get_text(strip=True).split(' -')
                elem_json['server'] = server_lang[0].lower()
                if len(server_lang) > 1: elem_json['language'] = '*%s' % server_lang[1].lower()
            if elem_json['server'].lower() in servers: elem_json['server'] = servers[elem_json['server'].lower()]
            if elem_json['server'].lower() in ["waaw", "jetload", "player"]: continue

            elem_json['title'] = '%s'

            elem_json['url'] = elem.iframe.get('data-src', '')
        except:
            logger.error(server)
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

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
        item.url = item.url + '?s=' + texto

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


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()

    try:
        if categoria in ['peliculas']:
            item.url = host + 'peliculas/'
        elif categoria == 'infantiles':
            item.url = host + 'animacion/?type=movies'
        elif categoria == 'terror':
            item.url = host + 'terror/?type=movies'
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
    