# -*- coding: utf-8 -*-
# -*- Channel MiTorrent -*-
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
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay', 
                       'BR-SCREEN', 'CAM', 'MicroHD', 'WEB', 'web-scr']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['torrent']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'mitorrent', 
             'host': config.get_setting("current_host", 'mitorrent', default=''), 
             'host_alt': ['https://mitorrent.me/'], 
             'host_black_list': ['https://startgaming.net/', 'https://mitorrent.eu/', 'https://mitorrent.org/'], 
             'status': '2023-03: En Search y Section no funciona la paginación en la web', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()
host_torrent = host
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/series'
language = ['LAT']
url_replace = []

finds = {'find': {'find': [{'tag': ['section']}], 'find_all': [{'tag': ['div'], 'class': ['browse-movie-wrap']}]}, 
         'sub_menu': {}, 
         'categories': {},  
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/|\/icono_(\w+))\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': {'find': [{'tag': ['div'], 'class': ['tsc_pagination']}], 
                       'find_all': [{'tag': ['a'], '@POS': [-2]}], 'get_text': [{'tag': '', '@STRIP': True}]}, 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find': [{'tag': ['div'], 'id': ['downloads']}], 'find_all': [{'tag': ['div'], 'class': ['accordion active']}]},
         'season_num': {'get_text': [{'tag': '', '@STRIP': True, '@TEXT': '(?i)temp\w*\s*(\d+)'}]}, 
         'seasons_search_num_rgx': [], 
         'seasons_search_qty_rgx': [], 
         'episode_url': '', 
         'episodes': {'find': [{'tag': ['div'], 'id': ['downloads']}], 'find_all': [{'tag': ['li']}]}, 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': {'find': [{'tag': ['div'], 'class': ['movie-info-fl-div movie-info-date']}], 
                        'find_next': [{'tag': ['div'], 'class': ['movie-info-fl-div movie-info-date']}], 
                        'find_next': [{'tag': ['div'], 'class': ['movie-info-fl-div movie-info-date']}], 
                        'find_all': [{'tag': ['a'], 'class': ["quality-download"]}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*imax', ''],
                         ['(?i)[\[|\(]?\d{3,4}p[\]|\)]?|[\[|\(]?(?:4k|3d|uhd|hdr)[\]|\)]?', ''], 
                         ['(?i)[-|\(]?\s*HDRip\)?|microHD|\(?BR-LINE\)?|\(?HDTS-SCREENER\)?', ''], 
                         ['(?i)\(?BDRip\)?|\(?BR-Screener\)?|\(?DVDScreener\)?|\(?TS-Screener\)?|[\(|\[]\S*\.*$', ''],
                         ['(?i)Castellano-*|Ingl.s|Trailer|Audio|\(*SBS\)*|\[*\(*dvd\s*r\d*\w*\]*\)*|[\[|\(]*dv\S*[\)|\]]*', ''], 
                         ['(?i)Dual|Subt\w*|\(?Reparado\)?|\(?Proper\)?|\(?Latino\)?|saga(?:\s*del)?', ''], 
                         ['(?i)(?:\s*&#8211;)?\s*temp.*?\d+.*', ''], ['\d?\d?&#.*', ''], ['\d+[x|×]\d+.*', ''], 
                         ['[\(|\[]\s*[\)|\]]', ''], ['(?i)(?:libro|volumen)?\s+\d{1,2}$', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', ''], 
                           ['(?i)\s*latino|\s*castellano|\s*dual|\s*Bittorrent\s*-\s*', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 21, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
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

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", 
                         c_type='peliculas', url=host + "peliculas/", thumbnail=get_thumb("channels_movie.png")))
    itemlist.append(Item(channel=item.channel, title="    - por Calidad", action="section", 
                         c_type='peliculas', url=host + "peliculas/", thumbnail=get_thumb("channels_movie_hd.png")))
    itemlist.append(Item(channel=item.channel, title="    - por Año", action="section", 
                         c_type='peliculas', url=host + "peliculas/", thumbnail=get_thumb("years.png")))
    itemlist.append(Item(channel=item.channel, title="    - por Idioma", action="section", 
                         c_type='peliculas', url=host + "peliculas/", thumbnail=get_thumb("channels_vos.png")))

    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", 
                         c_type='series', url=host + "series/", thumbnail=get_thumb("channels_tvshow.png")))
    itemlist.append(Item(channel=item.channel, title="    - por Año", action="section", 
                         c_type='series', url=host + "series/", thumbnail=get_thumb("years.png")))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", 
                         c_type='search', thumbnail=get_thumb("search.png")))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                         folder=False, thumbnail=get_thumb("next.png")))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                         thumbnail=get_thumb("setting_0.png")))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)                                # Activamos Autoplay

    return itemlist


def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()


def section(item):
    logger.info()

    findS = finds.copy()

    if 'Calidad' in item.title:
        findS['categories'] = {'find': [{'tag': ['select'], 'id': ['tax_calidad']}], 
                               'find_all': [{'tag': ['option'], 'value': True}]}

    elif 'Año' in item.title:
        findS['categories'] = {'find': [{'tag': ['select'], 'id': ['tax_ano']}], 
                               'find_all': [{'tag': ['option'], 'value': True}]}
        findS['controls'].update({'reverse': True})

    elif 'Idioma' in item.title:
        findS['categories'] = {'find': [{'tag': ['select'], 'id': ['tax_masopciones']}], 
                               'find_all': [{'tag': ['option'], 'value': True}]}

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        logger.error(elem)
        
        quality = year = language = ''

        elem_json['title'] = elem.get_text(strip=True).replace('todos', '')
        if not elem_json['title']: continue
        
        if 'Calidad' in item.title:
            quality = elem.get('value', '')
            elem_json['quality'] = '*%s' % elem_json['title']
        if 'Año' in item.title:
            year = elem.get('value', '')
        if 'Idioma' in item.title:
            language = elem.get('value', '')
            elem_json['language'] = '*%s' % elem_json['title']

        elem_json['url'] = '%ssearch-result/?search_query=&calidad=%s&genero=&dtyear=%s&audio=%s' \
                            % (host, quality, year, language)

        matches.append(elem_json.copy())

    return matches


def list_all(item):
    logger.info()
                
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['thumbnail'] = elem.img.get("data-src", "")
            elem_json['url'] = elem.a.get("href", "")
            elem_json['title'] = elem.find('div', class_='browse-movie-bottom').a.get_text(strip=True)
            if '1 año' in elem_json['title']: continue
            elem_json['year'] = elem.find('div', class_='browse-movie-year').get_text(strip=True)
            elem_json['language'] = '*%s' % elem.find('div', class_='browse-movie-tags').get_text(strip=True)

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if item.c_type == 'peliculas' and tv_path in elem_json['url']: continue
        if item.c_type == 'series' and movie_path in elem_json['url']: continue
        if not elem_json.get('url'): continue

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
    kwargs['headers'] = {'Referer': item.url}

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, generictools=True, finds=finds, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)
        
        elem_json['url'] = elem.a.get('href', '')
        elem_json['season']  = item.contentSeason
        elem_json['episode'] = int(scrapertools.find_single_match(elem.get_text(strip=True), '(?i)cap\w*\s+(\d+)') or 1)
        if scrapertools.find_single_match(elem.get_text(strip=True), '(?i)\d+x\d+-(\d+)'):
            elem_json['title'] = 'al %s' % scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)')
        elem_json['language'] = '*'
        elem_json['quality'] = '*'
        elem_json['torrent_info'] = ''
        elem_json['server'] = 'torrent'

        if not elem_json.get('url', ''): 
            continue

        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches
    
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    videolibrary = AHkwargs.get('videolibrary', False)

    if videolibrary:
        for x, (scrapedquality, scrapedsize, scrapedurl) in enumerate(matches_int):
            elem_json = {}
            #logger.error(matches_int[x])

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = item.infoLabels['episode']

            elem_json['url'] = scrapedurl
            elem_json['server'] = 'torrent'
            elem_json['language'] = '*'
            elem_json['quality'] = '*%s' % scrapedquality
            elem_json['torrent_info'] = scrapedsize

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        findS_findvideos = {'find_all': [{'tag': ['div'], 'class': ['modal-torrent']}]}
        torrent_info = AlfaChannel.parse_finds_dict(AlfaChannel.response.soup, findS_findvideos, c_type=item.c_type)

        for size, elem in zip(torrent_info, matches_int):
            elem_json = {}
            #logger.error(size)
            #logger.error(elem)
            
            try:
                elem_json['url'] = elem.get('href', '')
                elem_json['language'] = '*%s' % elem.get_text(strip=True)
                elem_json['quality'] = '*%s' % elem.get_text(strip=True).replace('1080p', '1080').replace('1080', '1080p')\
                                                                        .replace('1080_dual', '1080p')\
                                                                        .replace('720p', '720').replace('720', '720p')
                elem_json['torrent_info'] = size.find('p').find_next('p').get_text(strip=True)
                elem_json['server'] = 'torrent'

            except:
                logger.error(size)
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

    texto = texto.replace(" ", "+")
    
    try:
        item.url = '%ssearch-result/?search_query=%s&calidad=&genero=&dtyear=&audio=' % (host, texto)

        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []
 
 
def newest(categoria, **AHkwargs):
    logger.info()
    global kwargs
    kwargs = AHkwargs

    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel
    
    try:
        if categoria in ['peliculas', 'latino', 'torrent']:
            item.url = host + 'peliculas/'
            item.c_type = "peliculas"
            item.extra = "novedades"
            item.action = "list_all"
            itemlist.extend(list_all(item))
                
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
        
        if categoria in ['series', 'latino', 'torrent']:
            item.category_new= 'newest'
            item.url = host + "series/"
            item.c_type = "series"
            item.extra = "novedades"
            item.action = "list_all"
            itemlist.extend(list_all(item))

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
