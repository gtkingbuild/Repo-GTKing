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
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {'mx': 'Latino', 'dk': 'Latino', 'es': 'Castellano', 'en': 'VOSE', 'gb': 'VOSE', 
           'sub': 'VOSE', 'su': 'VOSE', 'eng': 'VOSE', "subtitulado": "VOSE", "usa": "VOSE", 
           'de': 'VOSE', "español": "Castellano", "espana": "Castellano", 'cas': 'Castellano', 
           "mexico": "Latino", "latino": "Latino", 'lat': 'Latino', 'LAT': 'Latino', 'jp': 'VOSE',
           'spain': 'Castellano'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['gvideo', 'fembed']
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'poseidonhd', 
             'host': config.get_setting("current_host", 'poseidonhd', default=''), 
             'host_alt': ["https://www.poseidonhd2.com/"], 
             'host_black_list': ["https://tekilaz.co/"], 
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
url_replace = [("/series/", "/serie/")]

finds = {'find': {'find': [{'tag': ['ul'], 'class': ['MovieList Rows', 'MovieList Rows episodes']}], 
                  'find_all': [{'tag': ['li'], 'class': ['TPostMv']}]},
         'categories': {'find': [{'tag': ['li'], 'id': ['menu-item-1953']}], 'find_all': [{'tag': ['li']}]}, 
         'search': {}, 
         'get_language': {'find_all': [{'tag': ['span'], 'class': ['flag']}]}, 
         'get_language_rgx': '(?:flags\/|-)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': {'find': [{'tag': ['a'], 'class': ['next page-numbers']}], 
                       'find_previous': [{'tag': ['span'], 'class': ['page-link'], '@TEXT': '(\d+)'}]}, 
         'year': {'find': [{'tag': ['span']}], 'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'season_episode': {'find': [{'tag': ['img'], '@ARG': 'alt', '@TEXT': '(?i)(\d+x\d+)'}]}, 
         'seasons': {'find': [{'tag': ['select'], 'id': ['select-season']}], 'find_all': [{'tag': ['option']}]}, 
         'season_num': {}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find': [{'tag': ['script'], 'id': ['__NEXT_DATA__']}], 'get_text': [{'tag': '', '@STRIP': False, '@JSON': 'DEFAULT'}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {'find': [{'tag': ['div'], 'class': ['Description']}, {'tag': ['p']}], 'get_text': [{'tag': '', '@STRIP': True}]}, 
         'findvideos': {'find': [{'tag': ['script'], 'id': ['__NEXT_DATA__']}], 'get_text': [{'tag': '', '@STRIP': False, '@JSON': 'DEFAULT'}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host+'peliculas/', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host+'series/', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

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


def section(item):
    logger.info()

    return AlfaChannel.section(item, **kwargs)


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
            if item.c_type == 'episodios':
                sxe = AlfaChannel.parse_finds_dict(elem, findS.get('season_episode', {}), c_type=item.c_type)
                elem_json['season'], elem_json['episode'] = sxe.split('x')
                elem_json['season'] = int(elem_json['season'] or 1)
                elem_json['episode'] = int(elem_json['episode'] or 1)
                elem_json['year'] = '-'

            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.img.get('alt', '') if item.c_type != 'episodios' else elem.img.get('alt', '').replace(sxe, '').strip()
            elem_json['thumbnail'] = elem.img.get('src', '')
            elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))
            if findS.get('plot', {}) and AlfaChannel.parse_finds_dict(elem, findS.get('plot', {}), c_type=item.c_type):
                elem_json['plot'] = AlfaChannel.parse_finds_dict(elem, findS.get('plot', {}), c_type=item.c_type)
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


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

    if not isinstance(matches_int, dict): matches_int = jsontools.load(matches_int)
    matches_int = matches_int.get('props', {}).get('pageProps', {}).get('thisSerie', {}).get('seasons', {})

    for x, elem_season in enumerate(matches_int):

        if item.contentSeason != elem_season.get('number', 1): continue
        for elem in elem_season.get('episodes', []):
            elem_json = {}
            #logger.error(elem)

            try:
                elem_json['url'] = elem.get('url', {}).get('slug', '').replace('seasons', 'temporada').replace('episodes', 'episodio')
                elem_json['title'] = elem.get('title', '')
                elem_json['season'] = item.contentSeason
                elem_json['episode'] = int(elem.get('number', '1') or '1')
                elem_json['thumbnail'] = elem.get('image', '')
            except:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

            if not elem_json.get('url', ''): 
                continue

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
    if not isinstance(matches_int, dict): matches_int = jsontools.load(matches_int)

    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem", "embed": "mystream"}
    action = item.contentType if item.contentType == 'episode' else 'thisMovie' if item.contentType == 'movie' else 'thisSerie'

    matches_int = matches_int.get('props', {}).get('pageProps', {}).get(action, {}).get('videos', [])

    for lang, elem in list(matches_int.items()):

        for link in elem:
            elem_json = {}
            #logger.error(elem)

            try:
                elem_json['server'] = link.get('cyberlocker', '')
                elem_json['url'] = link.get('result', '')
                elem_json['language'] = '*%s' % lang
                elem_json['quality'] = '*%s' % link.get('quality', '')
                elem_json['title'] = '%s'
            except:
                logger.error(link)
                logger.error(traceback.format_exc())
                continue

            if not elem_json['url']: continue

            if elem_json['server'].lower() in ["waaw", "jetload"]: continue
            if elem_json['server'].lower() in servers:
               elem_json['server'] = servers[elem_json['server'].lower()]

            matches.append(elem_json.copy())

    return matches, langs


def play(item):
    logger.info()

    itemlist = list()
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': -1, 
              'CF': False, 'cf_assistant': False, 'canonical': {}}
    
    try:
        data = AlfaChannel.create_soup(item.url, forced_proxy_opt=forced_proxy_opt, **kwargs).find("script")
        data = url = scrapertools.find_single_match(str(data), "url\s*=\s*'([^']+)'")
        
        if not data.startswith('http'):
            base_url = "%sr.php" % host
            post = {"data": data}
            kwargs['soup'] = False
            url = AlfaChannel.create_soup(base_url, post=post, forced_proxy_opt=forced_proxy_opt, **kwargs).url
            if not url: return itemlist
        
        if "fs.%s" % host.replace("https://", "") in url:
            api_url = "%sr.php" % host.replace("https://", "https://fs.")
            v_id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")
            post = {"h": v_id}
            kwargs['soup'] = False
            url = AlfaChannel.create_soup(api_url, post=post, forced_proxy_opt=forced_proxy_opt, **kwargs).url
        
        itemlist.append(item.clone(url=url, server=""))
        itemlist = servertools.get_servers_itemlist(itemlist)
    except:
        logger.error(traceback.format_exc())

    return itemlist


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    global kwargs
    kwargs = AHkwargs

    try:
        texto = texto.replace(" ", "+")
        item.url = host + 'search?q=' + texto

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
    global kwargs
    kwargs = AHkwargs

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
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
