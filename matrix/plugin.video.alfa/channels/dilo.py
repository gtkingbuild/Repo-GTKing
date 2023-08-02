# -*- coding: utf-8 -*-
# -*- Channel Dilo -*-
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

IDIOMAS = {'Español': 'CAST', 'Latino': 'LAT', 'Subtitulado': 'VOSE', 'en_es': 'VOSE', 
           'es': 'CAST', 'la': 'LAT', 'en': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_quality_movies = []
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['openload', 'streamango', 'powvideo', 'clipwatching', 'streamplay', 'streamcherry', 'gamovideo']
forced_proxy_opt = 'ProxyCF|CHECK'

canonical = {
             'channel': 'dilo', 
             'host': config.get_setting("current_host", 'dilo', default=''), 
             'host_alt': ["https://www.dilo.nu/"], 
             'host_black_list': ["https://streamtape.com/", "https://upstream.to/", "https://vidoza.net/", "http://vidoza.net/"], 
             'pattern': '<link\s*rel="stylesheet"\s*href="([^"]+)"', 
             'pattern_proxy': '{"item_id":\s*(\d+)}', 'proxy_url_test': 'breaking-bad/', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 30
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/catalogue'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['row fix-row', 'row vZDWbeaaab']}]), 
                       ('find_all', [{'tag': ['div'], 'class': ['col-lg-2', 'col-lg-3']}])]),
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/|languajes\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\?\&page=\d+', '?&page=%s']], 
         'last_page': dict([('find', [{'tag': ['a'], 'aria-label': re.compile('(?i)Netx')}]), 
                            ('find_previous', [{'tag': ['a']}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'year': {}, 
         'season_episode': dict([('find', [{'tag': ['div'], 'class': False}]), 
                                 ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(?i)(\d+x\d+)'}])]), 
         'seasons': {}, 
         'season_num': {'find': [{'tag': ['a'], '@ARG': 'data-season'}]}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'id': ['watch']}]), 
                             ('find_all', [{'tag': ['a'], 'class': ['border-bottom']}])]), 
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

    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos capitulos", action="list_all", url=host,
                         c_type='episodios', thumbnail=get_thumb('new episodes', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all",  url=host + 'catalogue?sort=latest',
                         c_type='series', thumbnail=get_thumb('last', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Mas vistas", action="list_all", url=host + 'catalogue?sort=mosts-week',
                         c_type='series', thumbnail=get_thumb('more watched', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host + 'catalogue',
                         c_type='series', thumbnail=get_thumb('all', auto=True)))

    itemlist.append(Item(channel=item.channel, title="- Géneros", action="section", url=host + 'catalogue', 
                         c_type='series', thumbnail=get_thumb('genres', auto=True)))

    itemlist.append(Item(channel=item.channel, title="- Por Años", action="section", url=host + 'catalogue',
                         c_type='series', thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="- Por País", action="section", url=host + 'catalogue',
                         c_type='series', thumbnail=get_thumb('country', auto=True)))

    itemlist.append(Item(channel=item.channel, title = 'Buscar...', action="search", url= host+'search?s=',
                         thumbnail=get_thumb('search', auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if 'Años' in item.title:
        findS['categories'] = dict([('find', [{'tag': ['button'], 'string': re.compile('(?i)Todos\s*los\s*a.os')}]), 
                                    ('find_previous', [{'tag': ['div'], 'class': ['dropdown YaGWbeaaab']}]), 
                                    ('find_all', [{'tag': ['div'], 'class': ['custom-control']}])])

    elif 'País' in item.title:
        findS['categories'] = dict([('find', [{'tag': ['button'], 'string': re.compile('(?i)Todos\s*los\s*pa.ses')}]), 
                                    ('find_previous', [{'tag': ['div'], 'class': ['dropdown YaGWbeaaab']}]), 
                                    ('find_all', [{'tag': ['div'], 'class': ['custom-control']}])])

    elif 'Géneros' in item.title:
        findS['categories'] = dict([('find', [{'tag': ['button'], 'string': re.compile('(?i)Todos\s*los\s*g.neros')}]), 
                                    ('find_previous', [{'tag': ['div'], 'class': ['dropdown YaGWbeaaab']}]), 
                                    ('find_all', [{'tag': ['div'], 'class': ['custom-control']}])])

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    dia_hoy = datetime.date.today()
    year = dia_hoy.year

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = url = '%s?%s=%s' % (item.url, elem.find('input').get('name', ''), 
                                                   elem.find('input').get('id', '').replace('-', '%20'))
            elem_json['title'] = elem.label.get_text(strip=True)
            if elem_json['title'].lower() in ['libros', 'musica', 'audiolibros', 'juego pc', 
                                              'juegos pc', 'onlyfans', 'software portable', 'pelicula'] \
                                              or not elem_json['title']: continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        matches.append(elem_json.copy())
    
    try:
        if 'Años' in item.title and matches:
            year_act = int(matches[0]['title'])
            while year_act < year:
                matches.insert(0, {'url': '%s?year[]=%s' % (item.url, str(year_act+1)), 'title': str(year_act+1)})
                year_act += 1
    except:
        logger.error(elem)
        logger.error(traceback.format_exc())

    return matches or matches_int


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    dia_hoy = datetime.date.today()
    year = str(dia_hoy.year)
    title_clean = '(?i)-%s-|\/va-|-pc-|v\d+\.|onlyfans|mp3' % year

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get("href", "")
            elem_json['thumbnail'] = elem.img.get('src', '')
            
            if item.c_type == 'episodios':
                sxe = AlfaChannel.parse_finds_dict(elem, findS.get('season_episode', {}), c_type=item.c_type)
                try:
                    elem_json['season'], elem_json['episode'] = sxe.split('x')
                    elem_json['season'] = int(elem_json['season'] or 1)
                    elem_json['episode'] = int(elem_json['episode'] or 1)
                except:
                    elem_json['season'] = 1
                    elem_json['episode'] = 1
                elem_json['title'] = elem.find('div', class_="font-weight-500").get_text(strip=True)
                if scrapertools.find_single_match(elem_json['url'], title_clean): continue
                if scrapertools.find_single_match(elem_json['title'], title_clean): continue

            else:
                elem_json['title'] = elem.find('div', class_="text-white").get_text(strip=True)
                elem_json['year'] = elem.find('div', class_="txt-gray-200").get_text(strip=True)
                elem_json['plot'] = elem.find('div', class_="description").get_text(strip=True)
                if scrapertools.find_single_match(elem_json['url'], title_clean): continue
                if scrapertools.find_single_match(elem_json['title'], title_clean): continue
                if elem_json['title'].lower() in ['libros', 'musica', 'audiolibros', 'juego pc', 
                                                  'juegos pc', 'onlyfans', 'software portable', 'pelicula'] \
                                                  or not elem_json['title']: continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()
    
    matches = []
    kwargs['soup'] = False

    data = AlfaChannel.create_soup(item.url, **kwargs).data

    item_id = scrapertools.find_single_match(data, '{"item_id":\s*(\d+)}')
    kwargs['post'] = AlfaChannel.do_urlencode({'item_id': item_id})
    kwargs['headers'] = {'Referer':item.url}
    kwargs['soup'] = False
    url = '%sapi/web/seasons.php' % host

    json_matches = AlfaChannel.create_soup(url, **kwargs).json

    for elem in json_matches:
        elem_json = {}
        #logger.error(elem)

        elem_json['season'] = int(elem.get('number', 0))
        elem_json['url'] = '%sapi/web/episodes.php' % host
        elem_json['post'] = AlfaChannel.do_urlencode({'item_id': item_id, 'season_number': elem_json['season']})
        elem_json['headers'] = {'Referer': item.url}

        if not elem_json.get('url', ''): continue

        matches.append(elem_json.copy())

    return AlfaChannel.seasons(item, seasons_list=matches)


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
    kwargs['soup'] = False

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        if not isinstance(elem, (dict, _dict)): continue

        try:
            if elem.get('audio', '') == 'N/A' and not elem.get('picture', '') and not elem.get('description', ''): continue

            elem_json['url'] = elem.get('permalink', '').rstrip('/') + '/'
            
            elem_json['language'] = re.compile('src="([^"]+)"', re.DOTALL).findall(elem.get('audio', ''))
            AlfaChannel.get_language_and_set_filter(elem_json['language'], elem_json)
            try:
                elem_json['season'] = int(elem.get('season_number', 0))
                elem_json['episode'] = int(elem.get('number', 0))
            except:
                elem_json['season'] = item.contentSeason
                elem_json['episode'] = 1
            if item.contentSeason != elem_json.get('season', 0): continue
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

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.get('data-link', '')
            elem_json['server'] = elem.find('div', class_='font-weight-500').get_text(strip=True)

            elem_json['language'] = re.compile('src="([^"]+)"', re.DOTALL).findall(str(elem.find('span', class_='juM9Fbab')))
            AlfaChannel.get_language_and_set_filter(elem_json['language'], elem_json)

            elem_json['title'] = '%s'
        except:
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

    itemlist = []
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              'timeout': timeout, 'cf_assistant': False, 'canonical': {}, 'soup': False}

    if item.server not in ['openload', 'streamcherry', 'streamango']:
        item.server = ''

    try:
        new_data = AlfaChannel.create_soup(item.url, **kwargs).data
        if "gamovideo" in item.url:
            item.url = scrapertools.find_single_match(new_data, '<a href="([^"]+)"')
        else:
            new_enc_url = scrapertools.find_single_match(new_data, '<iframe\s*class=[^>]+src="([^"]+)"')

            try:
                item.url = AlfaChannel.create_soup(new_enc_url, follow_redirects=False, **kwargs).headers['location']
            except:
                if not 'jquery' in new_enc_url:
                    item.url = new_enc_url
    except:
        pass

    if not item.url:
        return []

    itemlist.append(item.clone())
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "+")
    item.url = host + 'search?s=' + texto
    
    try:
        if texto != '':
            item.c_type = "series"
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

