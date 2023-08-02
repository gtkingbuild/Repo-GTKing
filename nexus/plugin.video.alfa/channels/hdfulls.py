# -*- coding: utf-8 -*-
# -*- Channel HDFullS -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

import re
import traceback
if not PY3: _dict = dict; from collections import OrderedDict as dict

from core.item import Item
from core import servertools
from core import scrapertools
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {'lat': 'LAT', 'spa': 'CAST', 'esp': 'CAST', 'sub': 'VOSE', 'espsub': 'VOSE', 'engsub': 'VOS', 'eng': 'VO'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay',
                       'HD1080', 'HD720', 'HDTV', 'RHDTV']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['flix555', 'clipwatching', 'gamovideo', 'powvideo', 'streamplay', 'vidoza', 'vidtodo', 'uptobox']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'hdfulls', 
             'host': config.get_setting("current_host", 'hdfulls', default=''), 
             'host_alt': ["https://www.hdfull.it/"], 
             'host_black_list': ["https://hdfull.bz/", "https://www.hdfull.tw/", 
                                 "https://www.hdfull.app/", "https://hdfull.be/", "https://hdfull.fm/"], 
             'status': 'SIN CANONICAL NI DOMINIO', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/movie"
tv_path = '/show'
language = []
url_replace = []
plot = ''

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['span-6 inner-6 tt view']}]}, 
         'categories': {}, 
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:images\/|-)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/\d+\/?$', '/%s/']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'id': ['filter']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)\/$'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['ul'], 'class': ['filter']}]), 
                          ('find_all', [{'tag': ['li']}])]), 
         'season_num': dict([('find', [{'tag': ['a']}]), 
                             ('get_text', [{'tag': '', '@STRIP': False}])]), 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['div'], 'id': ['season-episodes']}]), 
                           ('find_all', [{'tag': ['div'], 'class': ['flickr item left home-thumb-item']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['show-details']}]), 
                             ('find_all', [{'tag': ['a']}])]), 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'jump_page': True}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


""" CACHING HDFULLS PARAMETERS """
try:
    js_url = AlfaChannel.urljoin(host, "static/style/js/jquery.hdfull.view.min.js")
    data_js_url = AlfaChannel.urljoin(host, "static/js/providers.js")
    import xbmcgui
    window = None
    window = xbmcgui.Window(10000)
    js_data = window.getProperty("AH_hdfulls_js_data")
    data_js = window.getProperty("AH_hdfulls_data_js")
except:
    js_data = ''
    data_js = ''
    try:
        window.setProperty("AH_hdfulls_js_data", js_data)
        window.setProperty("AH_hdfulls_data_js", data_js)
    except:
        logger.error(traceback.format_exc())


def mainlist(item):
    logger.info()

    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, action="sub_menu", title="Películas", url=host,
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas', plot=plot))

    itemlist.append(Item(channel=item.channel, action="sub_menu", title="Series", url=host,
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series', plot=plot))

    itemlist.append(Item(channel=item.channel, action="search", title="Buscar...",
                         thumbnail=get_thumb('search', auto=True), c_type='search'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = []

    if item.c_type == "peliculas":
        itemlist.append(Item(channel=item.channel, action="list_all", title="Todas las Películas", text_bold=True, 
                             url=host + "movies/date/1/",thumbnail=get_thumb('last', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title=" - [COLOR paleturquoise]Películas Estreno[/COLOR]",
                             url=host + "new-movies",  thumbnail=get_thumb('premieres', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title="- [COLOR paleturquoise]Películas Actualizadas[/COLOR]",
                             url=host + "updated-movies/date/1/", thumbnail=get_thumb('updated', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="section", title=" - [COLOR paleturquoise]Películas por Género[/COLOR]",
                             url=host + "movies", thumbnail=get_thumb('genres', auto=True), c_type=item.c_type, plot=plot, extra='Género'))

        itemlist.append(Item(channel=item.channel, action="section", title=" - [COLOR paleturquoise]Películas por Año[/COLOR]",
                             url=host + "movies", thumbnail=get_thumb('year', auto=True), c_type=item.c_type, plot=plot, extra='Año'))

        itemlist.append(Item(channel=item.channel, action="list_all", title="Todas las Películas (Rating IMDB)", text_bold=True,
                             url=host + "movies/imdb_rating/date/1/", thumbnail=get_thumb('recomended', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title="Todas las Películas (ABC)", text_bold=True,
                             url=host + "movies/abc/date/1/", thumbnail=get_thumb('alphabet', auto=True), c_type=item.c_type, plot=plot))

        

    if item.c_type == "series":
        itemlist.append(Item(channel=item.channel, action="list_all", title="Todas las Series", text_bold=True, 
                             url=host + "tv-shows/date/1/", thumbnail=get_thumb('last', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title=" - [COLOR paleturquoise]Novelas Estreno[/COLOR]", 
                             url=host + "tv-tags/soap/date/1/", thumbnail=get_thumb('telenovelas', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title=" - [COLOR paleturquoise]Animes Estreno[/COLOR]", 
                             url=host + "tv-tags/anime/date/1/", thumbnail=get_thumb('anime', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title=" - [COLOR paleturquoise]Doramas Estreno[/COLOR]", 
                             url=host + "tv-tags/dorama/date/1/", thumbnail=get_thumb('doramas', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="section", extra="Género", title=" - [COLOR paleturquoise]Series por Género[/COLOR]",
                             url=host + "tv-shows", thumbnail=get_thumb('genres', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title="Todas las Series (Rating IMDB)", text_bold=True, 
                             url=host + "tv-shows/imdb_rating/date/1/", thumbnail=get_thumb('recomended', auto=True), c_type=item.c_type, plot=plot))

        itemlist.append(Item(channel=item.channel, action="list_all", title="Todas las Series (ABC)", text_bold=True, 
                             url=host + "tv-shows/abc/date/1/", thumbnail=get_thumb('alphabet', auto=True), c_type=item.c_type, plot=plot))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    findS['categories'] = {'find_all': [{'tag': ['li'], 'class': ['dropdown'], 
                                         '@POS': [2] if item.extra == 'Año' else [0] if item.c_type == 'series' else [1]}, 
                                        {'tag': ['li']}]}
    findS['url_replace'] = [['($)', '/date/1/']]

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
            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.find("a", class_="link").get("title", "")
            elem_json['thumbnail'] = elem.img.get('src', '')
            elem_json['quality'] = '*'
            elem_json['language'] = '*'
            if elem.find("div", class_="left").find_all("img"):
                for lang in elem.find("div", class_="left").find_all("img"):
                    if lang.get("src", ""):
                        elem_json['language'] += '%s ' % lang.get("src", "")
                AlfaChannel.get_language_and_set_filter(elem_json['language'], elem_json)
            if elem.find('div', class_="right") and elem.find('div', class_="right").get_text('.', strip=True):
                elem_json['title_subs'] = elem.find('div', class_="right").get_text('.', strip=True).replace('0.0', '')
                if elem_json['title_subs']: elem_json['title_subs'] = ['[COLOR darkgrey][%s][/COLOR]' % elem_json['title_subs']]

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
            elem_json['url'] = elem.a.get("href", "")
            elem_json['season'] = item.contentSeason
            elem_json['episode'] = int(scrapertools.find_single_match(elem_json['url'], "episode-(\d+)"))
            elem_json['language'] = item.language
            elem_json['thumbnail'] = elem.find('img').get("src", "")
            #if '/no-cover' in  elem_json['thumbnail']: continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url', ''): continue
 
        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()
    global js_data, data_js

    kwargs['matches_post_episodes'] = episodesxseason_matches

    if not js_data or not data_js:
        window.setProperty("AH_hdfull_js_data", '')
        window.setProperty("AH_hdfull_data_js", '')
        
        js_data = AlfaChannel.create_soup(js_url, soup=False, hide_infobox=True).data
        if js_data:
            if window: window.setProperty("AH_hdfulls_js_data", js_data)
            logger.info('Js_data DESCARGADO', force=True)
        else:
            logger.error('Js_data ERROR en DESCARGA')
            return matches
        
        data_js = AlfaChannel.create_soup(data_js_url, soup=False, hide_infobox=True).data
        if data_js:
            if window: window.setProperty("AH_hdfulls_data_js", data_js)
            logger.info('Data_js DESCARGADO', force=True)
        else:
            logger.error('Data_js ERROR en DESCARGA')
            return matches

    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    if PY3:
        from lib import alfaresolver_py3 as alfaresolver
    else:
        from lib import alfaresolver

    matches = []
    findS = AHkwargs.get('finds', finds)
    soup = AHkwargs.get('soup', {})
    
    try:
        year = int(soup.find('div', class_="show-details").find('p').find('a').get_text(strip=True))
        if year and year != item.infoLabels.get('year', 0):
            AlfaChannel.verify_item_year(item, year)
    except Exception:
        pass

    provs = alfaresolver.jhexdecode(data_js)
    matches_int = jsontools.load(alfaresolver.obfs(AlfaChannel.response.data, js_data))

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if elem.get('provider', '') in provs:
                embed = provs[elem['provider']].get('t', '')
                elem_json['play_type'] = "Ver" if embed == 's' else "Descargar"
                elem_json['url'] = provs[elem['provider']].get('d', '') % elem.get('code', '')
                elem_json['language'] = IDIOMAS.get(elem.get('lang', '').lower(), elem.get('lang', ''))
                elem_json['quality'] = '%s%s' % ('*' if item.contentType != 'movie' else '', elem.get('quality', '').upper() if PY3 else \
                                                 unicode(elem.get('quality', ''), "utf8").upper().encode("utf8"))
                elem_json['title'] = '%s'
                elem_json['server'] = ''

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def get_page_num(item):
    logger.info()
    # Llamamos al método que salta al nº de página seleccionado

    return AlfaChannel.get_page_num(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        texto = texto.replace(" ", "+")
        item.post = {"menu": "search", "query": texto}
        item.url = host + "search"

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
