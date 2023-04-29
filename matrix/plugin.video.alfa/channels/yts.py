# -*- coding: utf-8 -*-
# -*- Channel YTS -*-
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

IDIOMAS = {'es': 'CAST', 'la': 'LAT', 'us': 'VOSE', 'ES': 'CAST', 'LA': 'LAT', 'US': 'VOSE', 
           'espaniol': 'CAST', 'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VOSE'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = []
list_servers = ['torrent']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'yts', 
             'host': config.get_setting("current_host", 'yts', default=''), 
             'host_alt': ["https://yts.mx/"], 
             'host_black_list': [], 
             'pattern': '<ul\s*class="nav-links">\s*<li>\s*<a\s*href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = host
channel = canonical['channel']
categoria = channel.capitalize()
URL_BROWSE = host + "browse-movies"

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/browse-movies"
tv_path = '/series'
language = ['VOSE']
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['browse-movie-wrap']}]}, 
         'sub_menu': {}, 
         'categories': {'find': [{'tag': ['select'], 'name': ['%s']}], 'find_all': [{'tag': ['option']}]},
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {'find': [{'tag': ['ul'], 'class': ['tsc_pagination']}], 
                       'find_all': [{'tag': ['a'], '@POS': [-1], 'string': re.compile('(?i)Next'), '@ARG': 'href'}]}, 
         'next_page_rgx': [['\?page=\d+', '?page=%s']], 
         'last_page': {}, 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {},
         'season_num': {}, 
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['modal-torrent']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 
                      'host_torrent': host_torrent, 'duplicates': []},
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel = item.channel,
                         title = "Explorar Películas",
                         action = "list_all",
                         extra = 0,
                         c_type = 'peliculas', 
                         thumbnail=get_thumb("channels_movie.png"), 
                         url = URL_BROWSE
                        ))

    itemlist.append(Item(channel = item.channel,
                         title = "Más Populares",
                         action = "list_all",
                         extra = 1,
                         c_type = 'peliculas', 
                         thumbnail=get_thumb("now_playing.png"), 
                         url = host 
                        ))  

    itemlist.append(Item(channel = item.channel,
                         title = " - Explorar por Géneros",
                         action = "section",
                         extra = 'genre',
                         c_type = 'peliculas', 
                         thumbnail=get_thumb("genres.png"), 
                         url = URL_BROWSE
                        ))

    itemlist.append(Item(channel = item.channel,
                         title = " - Explorar por Calidades",
                         action = "section",
                         extra = 'quality',
                         c_type = 'peliculas', 
                         thumbnail=get_thumb("channels_movie_hd.png"), 
                         url = URL_BROWSE
                        ))

    itemlist.append(Item(channel = item.channel,
                         title = " - Explorar por Idiomas",
                         action = "section",
                         extra = 'language',
                         c_type = 'peliculas', 
                         thumbnail=get_thumb("channels_vos.png"), 
                         url = URL_BROWSE
                        ))

    itemlist.append(Item(channel = item.channel,
                         title = " - Explorar por Años",
                         action = "section",
                         extra = 'year',
                         c_type = 'peliculas', 
                         thumbnail=get_thumb("years.png"), 
                         url = URL_BROWSE
                        ))

    itemlist.append(Item(channel = item.channel,
                         title = "Buscar...",
                         action = "search",
                         extra = 0,
                         c_type = 'search', 
                         thumbnail=get_thumb("search.png"), 
                         url = URL_BROWSE
                        ))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    findS['categories'] = {'find': [{'tag': ['select'], 'name': ['%s' % item.extra]}], 
                           'find_all': [{'tag': ['option']}]}

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        elem_json['title'] = elem.get_text(strip=True)
        if 'all' in elem_json['title'].lower() or 'todos' in elem_json['title'].lower(): continue

        if item.extra == "genre":
            elem_json['url'] = URL_BROWSE + '/0/all/' + elem.get('value', '') + '/0/latest/0/all'
        elif item.extra == "year": 
            elem_json['url'] = URL_BROWSE + '/0/all/all/0/latest/' + elem.get('value', '') + '/all'
        elif item.extra == "language": 
            elem_json['url'] = URL_BROWSE + '/0/all/all/0/latest/0/' + elem.get('value', '')
        else:
            elem_json['url'] = URL_BROWSE + '/0/' + elem.get('value', '') + '/all/0/latest/0/all'

        matches.append(elem_json.copy())

    return matches


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
            elem_json['thumbnail'] = elem.img.get("src", "")
            elem_info = elem.find('div', class_='browse-movie-bottom')
            elem_json['title'] = elem_info.a.get_text(strip=True)
            elem_json['title'] = re.sub('\[\w*\]', '', elem_json['title'])
            if elem_info.a.span: elem_json['language'] = '*%s' % elem_info.a.span.get_text(strip=True)
            elem_json['year'] = elem.find('div', class_='browse-movie-year').get_text(strip=True)

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json.get('url'): continue

        matches.append(elem_json.copy())

    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        try:
            elem_json['quality'] = '*%s' % elem.find("p", class_="quality-size").get_text(strip=True)
            elem_json['quality'] += '-%s' % elem.find("div", class_="modal-quality").get_text(strip=True)
            elem_json['torrent_info'] = elem.find("p", class_="quality-size")\
                                            .find_next("p", class_="quality-size").get_text(strip=True).replace('N/A', '')
            elem_json['url'] = elem.find('a', class_='magnet-download').get('href', '')
            elem_json['server'] = 'torrent'

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): 
            continue

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
    
    text = text.replace(" ", "%20")

    try:
        if text:
            item.url = URL_BROWSE + '/' + text + '/all/all/0/latest/0/all'
            item.c_type = 'peliculas'
            item.texto = texto
            itemlist = list_all(item)

            return itemlist
        else:
            return []

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []