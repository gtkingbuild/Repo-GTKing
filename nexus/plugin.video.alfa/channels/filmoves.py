# -*- coding: utf-8 -*-
# -*- Channel Filmoves -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-
# -*- coding: utf-8 -*-

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
             'channel': 'filmoves', 
             'host': config.get_setting("current_host", 'filmoves', default=''), 
             'host_alt': ["https://filmoves.net/"], 
             'host_black_list': ["https://www.filmoves.net/", "https://filmoves.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['main-peliculas'], '@POS': [-1]}, 
                               {'tag': ['div'], 'class': ['movie-box-1']}]}, 
         'categories': dict([('find', [{'tag': ['ul'], 'class': ['generos-menu']}]), 
                             ('find_all', [{'tag': ['li']}])]),
         'search': dict([('find', [{'tag': ['body'],}]), 
                         ('get_text', [{'tag': '', '@STRIP': False, '@JSON': 'data,m&s|DEFAULT'}])]), 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\?page=\d+', '?page=%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2]}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'year': {}, 
         'season_episode': '', 
         'seasons': {'find_all': [{'tag': ['ul'], 'id': re.compile("season-\d+")}]}, 
         'season_num': {}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['body']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'profile_labels': {},
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 24, 
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

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='list_all', url=host + 'peliculas', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Por Géneros[/COLOR]', action='section', url=host, 
                         thumbnail=get_thumb('genres', auto=True), c_type='peliculas', extra='Géneros'))

    itemlist.append(Item(channel=item.channel, title=' - [COLOR paleturquoise]Estrenos[/COLOR]', action='list_all', url=host + 'estrenos', 
                         thumbnail=get_thumb('newest', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series', action='list_all', url=host + 'series', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host, 
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    if item.c_type == 'search':
        kwargs['headers'] = {"x-requested-with": "XMLHttpRequest"}

    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.get('slug', '') or elem.a.get("href", "")
            elem_json['title'] = elem.get('title', '') or elem.a.p.get_text(strip=True)
            elem_json['thumbnail'] = elem.get('cover', '') or elem.a.figure.img.get("src", "")
            elem_json['year'] = elem.get('release_year', '') or elem.a.span.get_text(strip=True)
            if item.c_type == 'search': elem_json['mediatype'] = 'movie' if movie_path in elem_json['url'] else 'tvshow'

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    findS = finds.copy()
    findS['url_replace'] = [['(?i)(\/temp[^$]+$)', '']]

    return AlfaChannel.seasons(item, finds=findS, **kwargs)


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item, **AHkwargs):
    logger.info()
    
    soup = AHkwargs.get('soup', '')

    findS = finds.copy()
    findS['episodes'] = dict([('find', [{'tag': ['ul'], 'id': re.compile("season-%s"  % item.contentSeason)}]), 
                              ('find_all', [{'tag': ['article']}])])

    kwargs['matches_post_get_video_options'] = findvideos_matches

    return AlfaChannel.episodes(item, data=soup, matches_post=episodesxseason_matches, finds=findS, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get('href', '')
            try:
                elem_json['episode'] = int(elem.div.span.get_text(strip=True).split("x")[1] or '1')
            except:
                elem_json['episode'] = 1
            elem_json['season'] = item.contentSeason

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
    data = AlfaChannel.response.data
    matches_int = re.compile("(?i)video\[(\d+)\]\s+?=\s+?'[^>]*src=\"([^\"]+)\"", re.DOTALL).findall(data)

    for v_id, url in matches_int:
        elem_json = {}
        #logger.error('v_id: %s; url: %s' % (v_id, url))

        try:
            elem_json['url'] = url

            info = scrapertools.find_single_match(data, '<a\s*href="#option%s">([^<]+)</a>' % v_id).split('-')
            elem_json['language'] = '*%s' % info[0].strip()
            elem_json['quality'] = '*%s' % info[1].strip()

            elem_json['server'] = ''
            elem_json['title'] = '%s'

        except:
            logger.error('v_id: %s; url: %s' % (v_id, url))
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

    #soup = AlfaChannel.create_soup(host, alfa_s=True, **kwargs)
    #findS = {'find': [{'tag': ['meta'], 'name': ['csrf-token'], '@ARG': 'content'}]}
    #token = AlfaChannel.parse_finds_dict(soup, findS)

    texto = texto.replace(" ", "+")
    #item.url += "suggest?que=%s&_token=%s" % (texto, token)
    item.url += "suggest?que=%s" % (texto)

    try:
        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    item = Item()
    try:
        if categoria in ['peliculas', 'latino']:
            item.url = host + 'peliculas'
        elif categoria == 'infantiles':
            item.url = host + 'genero/animacion/'
        elif categoria == 'terror':
            item.url = host + 'genero/terror/'
        itemlist = list_all(item)
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
