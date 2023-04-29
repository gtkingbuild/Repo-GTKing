# -*- coding: utf-8 -*-
# -*- Channel SeriesFlix -*-
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

IDIOMAS = {"Latino": "LAT", "Castellano": "CAST", "Subtitulado": "VOSE", 'la': 'LAT', 'es': 'CAST', 'ca': 'CAST', 'us': 'VOSE'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['uqload', 'fembed', 'mixdrop', 'supervideo', 'mystream']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'seriesflix', 
             'host': config.get_setting("current_host", 'seriesflix', default=''), 
             'host_alt': ["https://seriesflix.video/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/movies/"
tv_path = '/series/'
language = []
url_replace = []

finds = {'find': {'find': [{'tag': ['ul'], 'class': ['MovieList']}], 
                  'find_all': [{'tag': ['article'], 'class': ['TPost B']}]},
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': {'find': [{'tag': ['nav', 'div'], 'class': ['wp-pagenavi']}, {'tag': ['i'], 'class': ['fa-arrow-right']}], 
                       'find_previous': [{'tag': ['a'], 'class': ['page-link']}], 'get_text': [{'tag': '', '@STRIP': True}]}, 
         'year': {'find': [{'tag': ['span'], 'class': ['Date']}], 'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['section'], 'class': ['SeasonBx AACrdn']}]}, 
         'season_num': {'find': [{'tag': ['a']}], 'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['tr'], 'class': ['Viewed']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find': [{'tagOR': ['div'], 'class': ['optns-bx']},
                                 {'tag': ['ul'], 'class': ['ListOptions']}], 
                                 'find_all': [{'tag': ['li', 'button']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real-*|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
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

    itemlist.append(Item(channel=item.channel, title="Ultimas", action="list_all", url=host + "ver-series-online/",
                         thumbnail=get_thumb("last", auto=True), c_type='series', first=0))

    itemlist.append(Item(channel=item.channel, title="Productoras", action="section", url=host, 
                         thumbnail=get_thumb("studio", auto=True), c_type='series', extra='Productoras'))

    itemlist.append(Item(channel=item.channel, title="Géneros", action="section", url=host,
                         thumbnail=get_thumb("genres", auto=True), c_type='series', extra='Géneros'))

    itemlist.append(Item(channel=item.channel, title="Alfabético", action="section", url=host,
                         thumbnail=get_thumb("alphabet", auto=True), c_type='series', extra='Alfabético'))

    itemlist.append(Item(channel=item.channel, title="Año", action="section", url=host,
                         thumbnail=get_thumb("year", auto=True), c_type='series', extra='Año'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True), c_type='search'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if item.extra == "Alfabético":
        itemlist = []

        for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:

            itemlist.append(item.clone(action="list_all", title=letra, url=host + 'letras/%s/' % letra.lower()))

        return itemlist

    if "Géneros" in item.extra:
        findS['categories'] = {'find': [{'tag': ['div'], 'id': ['toroflix_genres_widget-2']}], 
                               'find_all': [{'tag': ['li']}]}

    elif 'Año' in item.extra:
        findS['categories'] = {'find': [{'tag': ['select'], 'class': ['Select-Md']}], 
                               'find_all': [{'tag': ['option']}]}
        findS['controls'].update({'reverse': True})
        return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)

    elif 'Productoras' in item.extra:
        findS['categories'] = {'find': [{'tag': ['li'], 'id': ['menu-item-1888']}], 
                               'find_all': [{'tag': ['li']}]}
        return AlfaChannel.section(item, postprocess=section_post, finds=findS, **kwargs)

    return AlfaChannel.section(item, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        elem_json['title'] = elem.get_text(strip=True)
        elem_json['url'] = '%s?s=filter&years[]=%s' % (host, elem_json['title'])

        matches.append(elem_json.copy())

    return matches


def section_post(elem, new_item, item, **AHkwargs):
    logger.info()
    
    if 'TODAS LAS PRODUCTORAS' in new_item.title.upper():
        return {}
    
    return new_item


def list_all(item):
    logger.info()

    findS = finds.copy()
    
    if item.extra == "Alfabético":
        findS['find'] = {'find': [{'tag': ['tbody']}], 'find_all': [{'tag': ['tr']}]}
        findS['year'] = {'find': [{'tag': ['td'], 'string': re.compile(r"\d{4}")}], 
                         'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}]}

    return AlfaChannel.list_all(item, matches_post=list_all_matches, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.extra == "Alfabético":
                info = elem.find("td", class_="MvTbTtl")
                elem_json['url'] = info.a.get("href", '')
                elem_json['title'] = info.a.get_text(strip=True)
                elem_json['thumbnail'] = elem.find("td", class_="MvTbImg").a.img.get("src", '')
                elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))

            else:
                elem_json['url'] = elem.a.get("href", "")
                elem_json['title'] = elem.find(class_="Title").get_text(strip=True)
                elem_json['thumbnail'] = elem.find("img")
                elem_json['thumbnail'] = elem_json['thumbnail']["data-src"] if elem_json['thumbnail']\
                                                   .has_attr("data-src") else elem_json['thumbnail']["src"]
                elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))

            if elem.find('span', class_="Qlty"): 
                if not scrapertools.find_single_match(elem.find('span', class_="Qlty").get_text(strip=True), '(\d{4})'):
                    elem_json['quality'] = '*%s' % elem.find('span', class_="Qlty").get_text(strip=True)
            
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

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = item.contentSerieName
            try:
                elem_json['episode'] = int(elem.find("span", class_="Num").get_text(strip=True) or 1)
            except:
                elem_json['episode'] = 1
            elem_json['season'] = item.contentSeason
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

    servers = {"femax20": "fembed", "embed": "mystream", "dood": "doodstream", "server": "directo"}

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['url'] = "%s?trembed=%s&trid=%s&trtype=2" % (host, elem.get("data-key", ""), elem.get("data-id", ""))
            
            elem_json['server'] = elem.find("p", class_="AAIco-dns").text
            if elem_json['server'].lower() in servers: elem_json['server'] = servers[elem_json['server'].lower()]
            if elem_json['server'].lower() in ["waaw", "jetload", "player"]: continue
            
            if elem.find("p", class_="AAIco-language"):
                elem_json['language'] = '*%s' % elem.find("p", class_="AAIco-language").get_text(strip=True).split(' ')[1]
            
            if elem.find("p", class_="AAIco-equalizer"):
                elem_json['quality'] = '*%s' % elem.find("p", class_="AAIco-equalizer").get_text(strip=True).replace('HD ', '')
            
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

    itemlist = list()
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 
              'timeout': 5, 'cf_assistant': False, 'follow_redirects': False, 'headers': item.headers, 'canonical': {}, 
              'CF': False, 'forced_proxy_opt': forced_proxy_opt}

    url = AlfaChannel.create_soup(item.url, **kwargs).find("div", class_="Video").iframe.get("src", "")

    if "streamcheck" in url or "//sc." in url:
        api_url = "%sstreamcheck/r.php" % host
        v_id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")
        post = {"h": v_id}
        kwargs['soup'] = False
        
        resp = AlfaChannel.create_soup(api_url, post=post, proxy_retries=-0, count_retries_tot=0, **kwargs)
        
        if resp.code in AlfaChannel.REDIRECTION_CODES:
            url = resp.headers.get('Location', '') or resp.url

    itemlist.append(item.clone(url=url, server=""))
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    global kwargs
    kwargs = AHkwargs

    try:
        texto = texto.replace(" ", "+")
        if texto:
            item.url += "?s=" + texto
            item.first = 0
            item.c_type='search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
