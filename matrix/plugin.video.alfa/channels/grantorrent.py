# -*- coding: utf-8 -*-
# -*- Channel GranTorrent -*-
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

IDIOMAS = {'es': 'CAST', 'la': 'LAT', 'us': 'VOSE', 'ES': 'CAST', 'LA': 'LAT', 'US': 'VOSE', 
           'espaniol': 'CAST', 'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VOSE'}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['torrent']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'grantorrent', 
             'host': config.get_setting("current_host", 'grantorrent', default=''), 
             'host_alt': ["https://grantorrent.zip/"], 
             'host_black_list': ['https://grantorrent.bz/', 'https://grantorrent.fi/', 'https://grantorrent.si/', 
                                 'https://grantorrent.re/', 'https://grantorrent.ac/', 'https://grantorrent.ch/'], 
             'pattern': '<div\s*class="flex[^>]*>\s*<a\s*href="([^"]+)"[^>]*>\s*.nicio\s*<', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_torrent = host.replace('https://', 'https://files.')
channel = canonical['channel']
categoria = channel.capitalize()
modo_ultima_temp = config.get_setting('seleccionar_ult_temporadda_activa', channel)     # Actualización sólo últ. Temporada?
min_temp = modo_ultima_temp if not modo_ultima_temp else 'continue'
movies_sufix = 'peliculas/'
series_sufix = 'series_p/'

timeout = config.get_setting('timeout_downloadpage', channel)
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peliculas"
tv_path = '/series'
language = ['CAST']
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['movie-list']}]), 
                        ('find_all', [{'tag': ['div'], 'class': ['relative my-5 md:my-4']}])]), 
         'sub_menu': {}, 
         'categories': {},  
         'search': {}, 
         'get_language': {'find': [{'tag': ['img'], '@ARG': 'src'}]}, 
         'get_language_rgx': '(?:flags\/|\/icono_(\w+))\.(?:png|jpg|jpeg|webp)', 
         'get_quality': dict([('find', [{'tag': ['ul'], 'class': True}]), 
                              ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'get_quality_rgx': [], 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['nav'], 'role': ['navigation']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href', '@TEXT': '\/(\d+)\/'}])]), 
         'year': {}, 
         'season_episode': {}, 
         'seasons': {},
         'season_num': {}, 
         'seasons_search_num_rgx': [['(?i)-temp\w*-(\d+)\/$', None]], 
         'seasons_search_qty_rgx': [['(?i)(?:Temporada|Miniserie)(?:-(.*?)(?:\.|\/|-$|$))', None]], 
         'episode_url': '', 
         'episodes': dict([('find', [{'tag': ['tbody'], 'class': ['bg-neutral-800']}]), 
                           ('find_all', [{'tag': ['tr']}])]), 
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['tbody'], 'class': ['bg-neutral-800']}]), 
                             ('find_all', [{'tag': ['tr']}])]), 
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
         'controls': {'min_temp': min_temp, 'url_base64': True, 'add_video_to_videolibrary': True, 'cnt_tot': 15, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': True, 
                      'host_torrent': host_torrent, 'duplicates': [['(?i)(?:-temp\w*)?-\d+\/$', '']]},
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
                         url=host + movies_sufix, thumbnail=get_thumb("channels_movie.png"), 
                         c_type="peliculas", category=categoria))
    itemlist.append(Item(channel=item.channel, title="   -   por Calidad", action="section", 
                         url=host + movies_sufix, thumbnail=get_thumb("channels_movie_hd.png"), 
                         c_type="peliculas", extra="calidades", category=categoria))
    itemlist.append(Item(channel=item.channel, title="   -   por Género", action="section", 
                         url=host + movies_sufix, thumbnail=get_thumb("genres.png"), 
                         c_type="peliculas", extra="generos", category=categoria))

    # Buscar películas
    itemlist.append(Item(channel=item.channel, title="Buscar en Películas >>", action="search", 
                         url=host + movies_sufix, thumbnail=get_thumb("search.png"), c_type="search", 
                         extra="peliculas", category=categoria))
    
    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", 
                         url=host + series_sufix, thumbnail=get_thumb("channels_tvshow.png"), 
                         c_type="series", category=categoria))

    # Buscar series
    itemlist.append(Item(channel=item.channel, title="Buscar en Series >>", action="search", 
                         url=host + series_sufix, thumbnail=get_thumb("search.png"), c_type="search", 
                         extra="series", category=categoria))

    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                         folder=False, thumbnail=get_thumb("next.png")))
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                         thumbnail=get_thumb("setting_0.png")))
    
    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)
    
    autoplay.show_option(item.channel, itemlist)

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools

    ret = platformtools.show_channel_settings()

    return platformtools.itemlist_refresh()


def section(item):
    logger.info()

    findS = finds.copy()

    if 'generos' in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['ul'], 'class': ['flex flex-col space-y-2']}]), 
                                    ('find_all', [{'tag': ['li']}])])

    elif 'calidades' in item.extra:
        findS['categories'] = dict([('find', [{'tag': ['div'], 'id': ['bloque_cat']}]), 
                                    ('find_all', [{'tag': ['a']}])])

    return AlfaChannel.section(item, finds=findS, **kwargs)


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
            elem_json['url'] = elem.a.get("href", "")
            elem_json['title'] = elem.p.get_text(strip=True)
            elem_json['thumbnail'] = elem.img.get("src", "")
            elem_json['quality'] = '*%s' % elem.find('div', class_='bg-opacity-85').span.get_text(strip=True) \
                                           if elem.find('div', class_='bg-opacity-85 text-neutral-100 rounded-t-xl '\
                                           'text-xs font-medium px-2 py-2 text-center') else '*'
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

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

    return AlfaChannel.episodes(item, matches_post=episodesxseason_matches, generictools=True, finds=finds, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        logger.error(elem)

        for x, td in enumerate(elem.find_all('td')):
            if x == 1: 
                try:
                    season = 0
                    sxe = td.get_text(strip=True)
                    if scrapertools.find_single_match(sxe, '(?i)temp\w*\s+(\d+)\s+comp\w*'):
                        season = scrapertools.find_single_match(sxe, '(?i)temp\w*\s+(\d+)\s+comp\w*')
                        episode = 1
                    elif scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)'):
                        season, episode = scrapertools.find_single_match(sxe, '(?i)(\d+)x(\d+)')
                    else:
                        sxe = elem.find_all('td')[-1].a.get('href', '')
                        season, episode = scrapertools.find_single_match(sxe, '(?i)\[Cap\.(\d{1})(\d{2})\]')
                        elem_json['quality'] = '*%s' % td.get_text(strip=True).replace('N/A', '')\
                                                       .replace('HDRip', 'HDTV').replace('720p', 'HDTV-720p').replace('Dvdrip', 'HDTV') or 'HDTV'
                    if len(season) > 2:
                        pos = len(str(item.contentSeason)) * -1
                        season = season[pos:]
                    elem_json['season'] = int(season or 1)
                    elem_json['episode'] = int(episode or 1)
                    if elem_json['season'] != item.contentSeason: break
                    if scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)'):
                        elem_json['title'] = 'al %s' % scrapertools.find_single_match(sxe, '(?i)\d+x\d+-(\d+)')
                except:
                    logger.error(td)
                    logger.error(traceback.format_exc())
                    break
            
            if x == 0: 
                elem_json['language'] = '*%s' % td.img.get('src', '').replace('N/A', '')
                AlfaChannel.get_language_and_set_filter(td, elem_json)
            if x == 2 and not elem_json.get('quality'): elem_json['quality'] = '*%s' % td.get_text(strip=True).replace('N/A', '')\
                                                        .replace('HDRip', 'HDTV').replace('720p', 'HDTV-720p').replace('HDRip', 'HDTV') or 'HDTV'
            if x == 3:
                if td.p: elem_json['password'] = td.get_text(strip=True).replace('N/A', '').replace('Sin clave', '')
                else: elem_json['torrent_info'] = td.get_text(strip=True).replace('N/A', '')
            if x == 4: elem_json['url'] = td.a.get('href', '')
            if x == 5:
                if host_torrent not in elem_json['url'] and td.a and td.a.get('href', ''):
                    elem_json['url'] = td.a.get('href', '')

        if elem_json.get('season', 0) != item.contentSeason:
            continue
        if not elem_json.get('url', ''): 
            continue

        elem_json['server'] = 'torrent'
        elem_json['title'] = elem_json.get('title', '')
        elem_json['quality'] = AlfaChannel.find_quality(elem_json, item)

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
        for x, (scrapedlang, scrapedpassword, scrapedurl) in enumerate(matches_int):
            elem_json = {}
            #logger.error(matches_int[x])

            if item.infoLabels['mediatype'] in ['episode']:
                elem_json['season'] = item.infoLabels['season']
                elem_json['episode'] = item.infoLabels['episode']

            elem_json['url'] = scrapedurl
            elem_json['server'] = 'torrent'
            elem_json['language'] = '*%s' % scrapedlang.replace('N/A', '')
            elem_json['quality'] = '*'
            elem_json['torrent_info'] = ''
            elem_json['password'] = scrapedpassword.replace('N/A', '').replace('Sin clave', '')

            matches.append(elem_json.copy())
            item.emergency_urls[1][x] = elem_json.copy()

    else:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)
            
            try:
                for x, td in enumerate(elem.find_all('td')):
                    if x == 0: 
                        elem_json['language'] = '*%s' % td.img.get('src', '').replace('N/A', '')
                        AlfaChannel.get_language_and_set_filter(td, elem_json)
                    if x == 1: elem_json['quality'] = '*%s' % td.get_text(strip=True).replace('N/A', '')
                    if x == 2 and td.get_text(strip=True): elem_json['quality'] = '*%s' % td.get_text(strip=True).replace('N/A', '')
                    if x == 3: 
                        if td.p: elem_json['password'] = td.get_text(strip=True).replace('N/A', '').replace('Sin clave', '')
                        else: elem_json['torrent_info'] = td.get_text(strip=True).replace('N/A', '')
                    if x == 4: elem_json['url'] = td.a.get('href', '')
                    if x == 5:
                        if host_torrent not in elem_json['url'] and td.a and td.a.get('href', ''):
                            elem_json['url'] = td.a.get('href', '')

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


def get_page_num(item):
    logger.info()
    # Llamamos al método que salta al nº de página seleccionado

    return AlfaChannel.get_page_num(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    texto = texto.replace(" ", "+")

    if item.c_type == 'search':
        if "/series" in item.url:
            item.c_type = "series"
        else:
            item.c_type = "peliculas"
    
    if item.c_type == "series":
        item.url = host + series_sufix
    else:
        item.url = host + movies_sufix

    try:
        if texto:
            item.url = "%s?query=%s" % (item.url, texto)
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
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel

    try:
        for cat in ['peliculas', 'series', '4k']:
            if cat != categoria: continue
                
            item.extra = cat
            if cat == 'peliculas': 
                item.c_type = 'peliculas'
                item.url = host + movies_sufix
            if cat == 'series': 
                item.c_type = 'series'
                item.url = host + series_sufix

            item.action = "list_all"
            itemlist = list_all(item)

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
