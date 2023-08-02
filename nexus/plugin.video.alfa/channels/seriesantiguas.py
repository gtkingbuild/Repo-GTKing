# -*- coding: utf-8 -*-
# -*- Channel Series Antiguas -*-
# -*- Created for Alfa Addon -*-
# -*- By the Alfa Development Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
if not PY3: _dict = dict; from collections import OrderedDict as dict

from core.item import Item
from core import servertools
from core import scrapertools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {"Latino": "LAT"}
list_language = list(IDIOMAS.values())
list_quality = []
list_quality_movies = []
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = []

canonical = {
             'channel': 'seriesantiguas', 
             'host': config.get_setting("current_host", 'seriesantiguas', default=''), 
             'host_alt': ["https://seriesantiguas.com/"], 
             'host_black_list': ["https://www.seriesantiguas.com/"], 
             'pattern': ['<a\s*href="([^"]+)"[^>]*>\s*(?:Principal|M.s\s*vistas)\s*<\/a>'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
forced_proxy_opt = 'ProxyCF'

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/ver'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['progression-masonry-margins']}]), 
                       ('find_all', [{'tag': ['div'], 'class': ['progression-masonry-item']}])]), 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {'find': [{'tag': ['div'], 'class': ['nav-previous']}, {'tag': ['a'], '@ARG': 'href'}]}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': {}, 
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['ul'], 'class': ['video-tabs-nav-aztec nav']}]), 
                          ('find_all', [['li']])]), 
         'season_num': {}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['div'], 'id': ['aztec-tab-%s']}]), 
                           ('find_all', [{'tag': ['div'], 'class': ['progression-studios-season-item']}])]), 
         'episode_num': ['(?i)(\d+)\.\s*[^$]+$', '(?i)[a-z_0-9 ]+\s*\((?:temp|epis)\w*\s*(?:\d+\s*x\s*)?(\d+)\)'], 
         'episode_clean': [['(?i)\d+\.\s*([^$]+)$', None], ['(?i)([a-z_0-9 ]+)\s*\((?:temp|epis)\w*\s*(?:\d+\s*x\s*)?\d+\)', None]], 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['embed-code-remove-styles-aztec']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', ''],
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
    
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series de los 80s",
            action = "list_all",
            url = host + 'media-category/80s/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("year", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series de los 90s",
            action = "list_all",
            url = host + 'media-category/90s/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("year", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Series del 2000",
            action = "list_all",
            url = host + 'media-category/00s/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("year", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Todas las series",
            action = "list_all",
            url = host + 'series/', 
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("all", auto=True)
        )
    )
    itemlist.append(
        Item(
            channel = item.channel,
            title = "Buscar...",
            action = "search",
            url = host,
            fanart = item.fanart,
            c_type='series', 
            thumbnail = get_thumb("search", auto=True)
        )
    )

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

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
        
        elem_json['url'] = elem.a.get('href', '')
        elem_json['title'] = elem.h2.get_text(strip=True)
        elem_json['thumbnail'] = elem.img.get('src', '')
        elem_json['quality'] = '*'
        elem_json['language'] = '*'
        elem_json['year'] = elem_json.get('year', '-')

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    findS = finds.copy()
    item.url = item.url.rstrip('/') + '/'

    soup = AlfaChannel.create_soup(item.url)

    url =  soup.find('a', class_='video-play-button-single-aztec', string=re.compile("antigua"))
    url = url['href'] if url else ''
    if url: 
        item.url = url.rstrip('/') + '/'
        soup = {}
        findS['seasons'] = {'find': [{'tag': ['li'], 'class': ['megalist']}], 'find_all': [['li']]}

    return AlfaChannel.seasons(item, data=soup, finds=findS, **kwargs)

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
    findS = finds.copy()

    if '/search' in item.url:
        findS['episodes'] = dict([('find', [{'tag': ['div'], 'class': ['blog-posts hfeed clearfix']}]), 
                                  ('find_all', [{'tag': ['div'], 'class': ['post hentry']}])])
    else:
        findS['episodes']['find'][0]['id'][0] = findS['episodes']['find'][0]['id'][0] % str(item.contentSeason)

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, finds=findS, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for x, elem in enumerate(matches_int):
        elem_json = {}

        elem_json['url'] = elem.a.get('href', '')
        elem_json['title'] = elem.h2.get_text(strip=True)
        elem_json['thumbnail'] = elem.img.get('src', '')
        elem_json['quality'] = '*'
        elem_json['language'] = '*'
        elem_json['server'] = elem.get('server', '')
        elem_json['size'] = elem.get('size', '')

        if not elem_json.get('url', ''): 
            continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches
    findS = finds.copy()

    findS['controls'].update({'headers': {'Referer': host}})

    item.url = item.url.rstrip('/') + '/' if not item.url.endswith('.html') else item.url
    if not '/episodio' in item.url:
        findS['findvideos'] = {'find_all': [{'tag': ['div'], 'class': ['post-body entry-content']}]}

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, finds=findS, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        logger.error(elem)

        elem_json = {}
        
        elem_json['server'] = ''
        elem_json['url'] = elem.iframe.get('src', '')

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
        item.url = item.url + '?post_type=video_skrn&search_keyword=' + texto
        
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
