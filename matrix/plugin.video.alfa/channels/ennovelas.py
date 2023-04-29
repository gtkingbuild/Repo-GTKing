# -*- coding: utf-8 -*-
# -*- Channel Ennovelas -*-
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

IDIOMAS = {'la': 'LAT', 'sub': 'VOSE', 'es': 'CAST'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['fembed', 'mega', 'yourupload', 'streamsb', 'mp4upload', 'mixdrop', 'uqload']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'ennovelas', 
             'host': config.get_setting("current_host", 'ennovelas', default=''), 
             'host_alt': ["https://w.ennovelas.net/"], 
             'host_black_list': ["https://www.zonevipz.com/", "https://www.ennovelas.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/movies"
tv_path = '/series'
language = ['LAT']
url_replace = [['https://ennovelas.net/', host]]

finds = {'find': {'find_all': [{'tag': ['article'], 'class': 'post'}]},
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': {'find': [{'tag': ['div'], 'class': ['navigation']}], 
                       'find_all': [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)\/$'}]}, 
         'year': {}, 
         'season_episode': {},
         'seasons': {}, 
         'season_num': {}, 
         'seasons_search_num_rgx': [['(?i)-(?:t\w*-*)?(\d{1,2})(?:-a)?\/*$', None], ['(?i)-(\d{1,2})(?:-temp\w*|-cap[^$]*)?\/*$', None]], 
         'seasons_search_qty_rgx': None, 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['article'], 'class': 'postEp'}]},
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find': [{'tag': ['div'], 'id': ['btnServers']}], 'find_all': [{'tag': ['form']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)\s*(?:\s*–|-)?\s+(\d+)\s+(?:temp\w*\s+-*\s+)?cap.\w+\s+(\d+)', ''], 
                         ['(?i)(?:\s*–|-)?\s+cap.\w+\s+(\d+)', ''], ['(?i)(?:\s+\d+)?\s+temp\w*(?:\s+\d+)?', ''], 
                         ['\s+\d{1,2}$', ''], ['(?i)\s+“*final”*$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 17, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': True, 
                      'duplicates': [['(?i)-(?:t\w*-*)?(\d{1,2})(?:-a)?\/*$', ''], ['(?i)-(\d{1,2})(?:-temp\w*|-cap[^$]*)?\/*$', '']]},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = list()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", 
                         url=host + "movies/", c_type='peliculas', thumbnail=get_thumb("movies", auto=True)))

    itemlist.append(Item(channel=item.channel, title="Novelas", action="list_all", 
                         url=host + "telenovelas/", c_type='series', thumbnail=get_thumb("tvshows", auto=True)))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Nuevos Episodios[/COLOR]" , action="list_all", 
                         url= host + "capitulos-n1/", c_type='episodios', thumbnail=get_thumb('new_episodes', auto=True)))
    itemlist.append(Item(channel=item.channel, title=" - [COLOR paleturquoise]Por Países[/COLOR]" , action="section", 
                         url= host, c_type='series', thumbnail=get_thumb('country', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Por Años" , action="section", 
                         url= host, c_type='series', thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         c_type='search', thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if 'Países' in item.title:
        findS['categories'] = {'find': [{'tag': ['li'], 'id': 'menu-item-42726'}], 'find_all': [{'tag': ['li']}]}

    if 'Años' in item.title:
        findS['categories'] = {'find': [{'tag': ['li'], 'id': 'menu-item-42731'}], 'find_all': [{'tag': ['li']}]}

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
            elem_json['url'] = elem.find('a').get("href", "")
            elem_json['title'] = elem.find('a', title=True).get('title', '')
            elem_json['thumbnail'] = elem.find("img", class_='imgLoaded').get("data-img", "")
            
            if item.c_type == 'episodios':
                elem_json['season'] = 1
                if elem.find('span', class_='ribbon'):
                    if scrapertools.find_single_match(elem.find('span', class_='ribbon').get_text(strip=True), '\d+'):
                        elem_json['season'] = scrapertools.find_single_match(elem.find('span', class_='ribbon').get_text(strip=True), '\d+')
                    else:
                        elem_json['language'] = '*%s' % elem.find('span', class_='ribbon').get_text(strip=True)
                elem_json['episode'] = scrapertools.find_single_match(elem.find('div', class_='episodeNum').get_text('|', strip=True), '\d+')
                elem_json['season'] = int(elem_json['season'] or 1)
                elem_json['episode'] = int(elem_json['episode'] or 1)
                elem_json['language'] = elem_json.get('language', '*')

            elif tv_path not in elem_json['url'] and AHkwargs.get('function', '') == 'find_seasons':
                break
            elif tv_path not in elem_json['url'] and item.c_type == 'search':
                continue

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

    findS['controls'].update({'title_search': '%s temporada' % item.season_search or item.contentSerieName})

    return AlfaChannel.seasons(item, finds=findS, **kwargs)


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
            elem_json['url'] = elem.find('a').get("href", "")
            elem_json['season'] = item.contentSeason
            elem_json['episode'] = scrapertools.find_single_match(elem.find('div', class_='episodeNum').get_text('|', strip=True), '\d+')
            elem_json['episode'] = int(elem_json['episode'] or 1)
            elem_json['language'] = elem_json.get('language', '*')
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if elem_json.get('season', 0) != item.contentSeason: continue
        if not elem_json.get('url', ''): continue
 
        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              'timeout': 5, 'cf_assistant': False, 'canonical': {}}

    for elem_ini in matches_int:
        #logger.error(elem_ini)

        if elem_ini.input.get('name', '') != 'watch': continue
        url = elem_ini.get('action', '')
        post = 'watch=%s&submit=' % elem_ini.input.get('value', '')

        for elem in AlfaChannel.create_soup(url, post=post, **kwargs).find('ul', class_="serversList").find_all('li'):
            elem_json = {}
            #logger.error(elem)

            elem_json['url'] = elem.get('data-server', '')
            elem_json['url'] = scrapertools.find_single_match(elem_json['url'], "src='([^']+)'")
            if not elem_json.get('url', ''): continue
            if 'ennovelas' in elem_json['url'] or 'lvturbo' in elem_json['url'] or 'vidmoly' in elem_json['url'] \
                                               or 'sbface' in elem_json['url']:
                continue

            elem_json['title'] = '%s'
            elem_json['server'] = ''
            elem_json['language'] = '*'

            matches.append(elem_json.copy())

    return matches, langs


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
        item.url = '%ssearch/%s/' %  (host, texto)

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
