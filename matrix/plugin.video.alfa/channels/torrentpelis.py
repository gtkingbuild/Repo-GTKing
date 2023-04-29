# -*- coding: utf-8 -*-
# -*- Channel Torrentpelis -*-
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


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['torrent']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'torrentpelis', 
             'host': config.get_setting("current_host", 'torrentpelis', default=''), 
             'host_alt': ['https://torrentpelis.org/'], 
             'host_black_list': ['https://www2.torrentpelis.com/', 'https://www1.torrentpelis.com/', 'https://torrentpelis.com/'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
channel = canonical['channel']
categoria = channel.capitalize()

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/serie'
language = []
url_replace = []

finds = {'find': {'find': [{'tag': ['div'], 'id': ['archive-content', 'items normal']}], 
                  'find_all': [{'tag': ['article'], 'class': ['item']}]}, 
         'categories': {'find': [{'tag': ['ul'], 'class': ['sub-menu']}], 
                        'find_all': [{'tag': ['li']}]}, 
         'search': {'find_all': [{'tag': ['div'], 'class': ['result-item']}]}, 
         'get_language': {}, 
         'get_language_rgx': '(?:flags\/||d{4}\/\d{2}\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': {'find': [{'tag': ['div'], 'class': ['pagination']}, {'tag': ['span']}], 
                       'get_text': [{'@TEXT': '..gina \d+ de (\d+)'}]}, 
         'season_episode': {}, 
         'season': {}, 
         'season_num': {}, 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {}, 
         'episode_num': [], 
         'episode_clean': [], 
         'findvideos': {'find': [{'tag': ['tbody']}], 'find_all': [{'tag': ['tr']}]}, 
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie', ''], ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
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

    thumb_pelis = get_thumb("channels_movie.png")
    thumb_genero = get_thumb("genres.png")
    thumb_calidad = get_thumb("top_rated.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", c_type='peliculas', 
                url=host + 'peliculas/page/1/', thumbnail=thumb_pelis, extra2="PELICULA"))
    itemlist.append(Item(channel=item.channel, title="    - por Género", action="section", c_type='peliculas', 
                url=host, thumbnail=thumb_genero, extra2="GENERO"))
    itemlist.append(Item(channel=item.channel, title="    - por Tendencias", action="list_all", c_type='peliculas', 
                url=host + 'tendencias/page/1/', thumbnail=thumb_calidad, extra2="TENDENCIAS"))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                url=host, thumbnail=thumb_buscar, extra="search"))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                folder=False, thumbnail=thumb_separador))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                thumbnail=thumb_settings))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)                                #Activamos Autoplay

    return itemlist


def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()

    return


def section(item):
    logger.info()

    return AlfaChannel.section(item)


def list_all(item):
    logger.info()

    findS = finds.copy()

    if item.extra2 in ["GENERO", "TENDENCIAS"]: 
        findS['find'] = {
                         'find': [{'tag': ['div'], 'class': ['items normal']}], 
                         'find_all': [{'tag': ['article'], 'class': ['item']}]
                        }
    elif item.extra == "search":
        findS['find'] = findS.get('search', {})
                       
    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, finds=findS, **kwargs)
                        

def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        
        elem_json['url'] = elem.a.get('href', '')
        elem_json['title'] = elem.img.get('alt', '')
        elem_json['thumbnail'] = elem.img.get('src', '')
        if item.extra == "search":
            elem_json['year'] = elem.find('span', class_="year").text
        else:
            elem_json['year'] = elem.find('div', class_='data').find('span').text
        elem_json['year'] = scrapertools.find_single_match(elem_json['year'], '\d{4}')
        
        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()

    kwargs = item.kwargs = {'follow_redirects': False}

    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    videolibrary = AHkwargs.get('videolibrary', False)

    if videolibrary:
        for x, (scrapedurl, scrapedquality, scrapedlanguage, scrapedsize) in enumerate(matches_int):
            elem_json = {}

            elem_json['url'] = scrapedurl
            elem_json['server'] = 'torrent'
            elem_json['quality'] = scrapedquality
            elem_json['language'] = scrapedlanguage
            if not elem_json['quality'].startswith('*'): elem_json['quality'] = '*%s' % elem_json['quality']
            if not elem_json['language'].startswith('*'): elem_json['language'] = '*%s' % elem_json['language']
            elem_json['torrent_info'] = scrapedsize
            if '--' in elem_json['torrent_info']: elem_json['torrent_info'] = ''

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            elem_json = {}
            elem_json['server'] = 'torrent'

            for x, td in enumerate(elem.find_all('td')):
                if x == 0: elem_json['url'] = td.a['href']
                if x == 1: elem_json['quality'] = '*%s' % td.get_text()
                if x == 2: elem_json['language'] = '*'
                if x == 3: elem_json['torrent_info'] = td.get_text()
            
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
        item.url = host + '?s=' + texto
        item.extra = 'search'

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
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
            item.url = host + "peliculas/"
            item.extra = "peliculas"
            item.extra2 = "novedades"
            item.action = "list_all"
            itemlist.extend(list_all(item))
                
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []

    return itemlist
