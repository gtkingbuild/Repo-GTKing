# -*- coding: utf-8 -*-
# -*- Channel Playview -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
if not PY3: _dict = dict; from collections import OrderedDict as dict
import datetime

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {"Latino": "LAT", "Español": "CAST", "Subtitulado": "VOSE"}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['upstream', 'cloudvideo', 'mixdrop', 'mystream', 'doodstream']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'playview', 
             'host': config.get_setting("current_host", 'playview', default=''), 
             'host_alt': ["https://playview.io/"], 
             'host_black_list': [], 
             'pattern': '<link\s*rel="[^>]*icon"[^>]+href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '-temp'
language = []
url_replace = []
date = datetime.datetime.now()

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['spotlight_container']}]},
         'categories': dict([('find', [{'tag': ['ul'], 'class': ['mobile-nav']}]), 
                             ('find_all', [{'tag': ['li']}])]), 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\:\d+', '/page:%s']], 
         'last_page': dict([('find', [{'tag': ['a'], 'aria-label': 'Next'}]), 
                            ('find_previous', [{'tag': ['a'], 'class': ['page-link']}]), 
                            ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['a'], 'aria-label': ['Reproducir']}]}, 
         'season_num': {}, 
         'seasons_search_num_rgx': '(?i)-temp\w*-(\d+)', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['div'], 'class': ['episodeBlock']}]}, 
         'episode_num': [], 
         'episode_clean': [['(?i)ver\s*\d*\s*-*\s*', '']], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['button'], 'class': ['select-quality']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
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

    itemlist.append(Item(channel=item.channel, title='Películas', action='sub_menu',
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series', action='sub_menu',
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title='Buscar...', action='search', url=host + 'search/',
                         thumbnail=get_thumb('search', auto=True), c_type='search'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_movies + list_quality_tvshow)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    if item.c_type == 'peliculas':
        itemlist.append(Item(channel=item.channel, title='Todas', action='list_all', url=host + 'peliculas-online', 
                             thumbnail=get_thumb('all', auto=True), c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, title='Ultimas', action='list_all', url=host + 'estrenos-%s' % date.year, 
                             thumbnail=get_thumb('last', auto=True), c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, title='Próximamente', action='list_all', url=host + 'proximamente', 
                             thumbnail=get_thumb('newest', auto=True), c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, title='Generos', action='section', url=host, 
                             thumbnail=get_thumb('genres', auto=True), c_type=item.c_type))

    else:
        itemlist.append(Item(channel=item.channel, title='Todas', action='list_all', url=host + 'series-online',
                             thumbnail=get_thumb('tvshows', auto=True), c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, title='Series Animadas', action='list_all', url=host + 'series-animadas-online',
                             thumbnail=get_thumb('animacion', auto=True), c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, title='Anime', action='list_all', url=host + 'anime-online',
                             thumbnail=get_thumb('anime', auto=True), c_type=item.c_type))

        itemlist.append(Item(channel=item.channel, title='Doramas', action='list_all', url=host + 'dramas-online',
                             thumbnail=get_thumb('doramas', auto=True), c_type=item.c_type))

    return itemlist



def section(item):
    logger.info()

    return AlfaChannel.section(item, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get("href", "")
            elem_json['title'] = elem.a.get_text(strip=True)
            if elem_json['title'].lower() in ['próximos estrenos', 'series', 'series animadas', 'series anime'] \
                                              or not elem_json['title']: continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        matches.append(elem_json.copy())

    matches = sorted(matches, key=lambda i: i['title'])

    return matches or matches_int


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
            if item.c_type == 'search':
                elem_json['mediatype'] = 'movie' if elem.find('span', class_="slqual-HD") else 'tvshow'

            elem_json['title'] = elem.find('div', class_="spotlight_title").get_text('|', strip=True).split('|')[0]

            elem_json['thumbnail'] = elem.div.get('data-original', '')

            if elem.find('div', class_="spotlight_info"): 
                info = elem.find('div', class_="spotlight_info").get_text('|', strip=True).split('|')
                if item.c_type == 'peliculas': elem_json['quality'] = '*%s' % info[0]
                elem_json['year'] = info[1] if item.c_type == 'peliculas' else info[0]

            if elem_json['url'].endswith('ver-temporadas-completas-de/'):
                elem_json['url'] ="%sver-temporadas-completas-de/%s" % (host, elem_json['title'].lower().replace(' ', '-'))
            elif elem.find("div", class_="info-series"):
                season_path = re.sub("-temp-\d+", "", scrapertools.find_single_match(elem_json['url'], "%s(.+)" % host))
                elem_json['url'] = "%sver-temporadas-completas-de/%s" % (host, season_path)
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
    
    info_soup = AlfaChannel.create_soup(item.url)

    info = info_soup.find("div", id="ficha")
    kwargs['post'] = {"set": "LoadOptionsEpisode", 'action': "EpisodesInfo", "id": info["data-id"], "type": info["data-type"]}

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            try:
                elem_json['episode'] = int(elem.find("div", class_="episodeNumber").get_text(strip=True))
            except:
                elem_json['episode'] = 1
            elem_json['season'] = item.contentSeason
            elem_json['url'] = item.url
            elem_json['post'] = {"set": "LoadOptionsEpisode", "action": "Step1", "id": elem.get("data-id", ""), 
                                 "type": "1", 'episode': elem_json['episode']}
            elem_json['thumbnail'] = scrapertools.find_single_match(elem.find("div", class_="episodeImage").get('style', ''), 'url\(([^\)]+)\)')
            elem_json['title'] = elem.get("title", "")
            elem_json['plot'] = elem.find("div", class_="episodeSynopsis").get_text(strip=True)
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url', ''): continue
 
        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()

    if not item.post:
        info_soup = AlfaChannel.create_soup(item.url)
        info = info_soup.find("div", id="ficha")
        item.post = {"set": "LoadOptions", 'action': "Step1", "id": info["data-id"], "type": info["data-type"]}

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for step2 in matches_int:
        #logger.error(step2)
        
        kwargs['post'] = {"set": item.post["set"], "action": "Step2", "id": item.post["id"], "type": item.post["type"],
                          "quality": step2.get("data-quality", ""), "episode": item.post.get("episode", "")}

        soup = AlfaChannel.create_soup(item.url, **kwargs)
        
        for elem in soup.find_all("li", class_="tb-data-single"):
            elem_json = {}
            #logger.error(elem)

            try:
                elem_json['language'] = '*%s' % elem.find("h4").get_text(strip=True)

                elem_json['server'] = re.sub(r"(\..+|\s.+)", "", elem.find("img")["title"].lower()) or "directo"
                if elem_json['server'].lower() in ["waaw", "jetload", "player"]: continue

                elem_json['title'] = '%s'

                elem_json['url'] = host + canonical['channel']
                
                elem_json['post'] = {"set": item.post["set"], "action": "Step3", 
                                     "id": elem.find("button", class_="btn-link").get("data-id", ""), 
                                     "type": item.post["type"]}
                 
                elem_json['quality'] = '*%s' % scrapertools.find_single_match(step2.get("data-quality", ""), r"\d+p")

            except:
                logger.error(step2)
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


def play(item):
    logger.info()
    import base64

    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              'timeout': timeout, 'cf_assistant': False, 'canonical': {}, 'soup': False}

    url_data = AlfaChannel.create_soup(item.url, post=item.post)
    
    try:
        iframe = re.sub('https*:\/*\/*', 'https://', url_data.find("iframe", class_="embed-responsive-item")["src"])
        url = AlfaChannel.create_soup(iframe, **kwargs).url
    except:
        try:
            url_data = url_data.find("button", class_="linkfull").get("data-url", "")
            url = base64.b64decode(scrapertools.find_single_match(url_data, "/go/(.+)")).decode('utf-8')
        except:
            url = host

    srv = servertools.get_server_from_url(url)
    item = item.clone(url=url, server=srv)

    return [item]


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + texto

        if texto != '':
            item.c_type = 'search'
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys

        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item = Item()
    item.c_type = 'peliculas'
    
    try:
        if categoria == 'peliculas':
            item.url = host + 'peliculas-online'
        elif categoria == 'infantiles':
            item.url = host + 'peliculas-online/animacion'
        elif categoria == 'terror':
            item.url = host + 'peliculas-online/terror'

        itemlist = list_all(item)
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist




