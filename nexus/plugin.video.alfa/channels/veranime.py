# -*- coding: utf-8 -*-
# -*- Channel VerAnime -*-
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
from core import jsontools
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {"audio castellano": "CAST", "audio latino": "LAT", "subtitulado": "VOSE"}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ["aparatcam", "streamtape", "fembed", "mixdrop", "doodstream", "clipwatching"]
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'veranime', 
             'host': config.get_setting("current_host", 'veranime', default=''), 
             'host_alt': ["https://ww3.animeonline.ninja/"], 
             'host_black_list': ["https://ww2.animeonline.ninja/", "https://www1.animeonline.ninja/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant_if_proxy': True, 'cf_assistant_get_source': False, 'CF_stat': True, 'session_verify': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 15
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/pelicula"
tv_path = '/online'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tagOR': ['div'], 'id': ['archive-content']},
                                 {'tag': ['div'], 'class': ['items']}]), 
                       ('find_all', [{'tag': ['article'], 'id': re.compile("^post-\d+")}])]), 
         'categories': dict([('find', [{'tag': ['nav'], 'class': ['releases']}]), 
                             ('find_all', [{'tag': ['li']}])]),
         'search': {'find_all': [{'tag': ['div'], 'class': ['result-item']}]}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}, 
                                      {'tag': ['span']}]), 
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '\d*\s*de\s*(\d+)'}])]),  
         'year': {}, 
         'season_episode': {}, 
         'seasons': dict([('find', [{'tag': ['div'], 'id': ['seasons']}]), 
                          ('find_all', [{'tag': ['div'], 'class': ['se-c']}])]),
         'season_num': dict([('find', [{'tag': ['span'], 'class': ['se-t']}]), 
                             ('get_text', [{'tag': '', '@STRIP': True}])]),
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'season_url': host, 
         'episode_url': '%sepisodio/%s-%sx%s', 
         'episodes': dict([('find', [{'tag': ['div'], 'id': ['seasons']}]), 
                           ('find_all', [{'tag': ['div'], 'class': ['se-c']}])]),
         'episode_num': [], 
         'episode_clean': [], 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['ul'], 'id': ['playeroptionsul']}]), 
                             ('find_all', [{'tag': ['li']}])]),
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 29, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'IDIOMAS_TMDB': {0: 'es', 1: 'ja', 2: 'es'}}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()
    
    itemlist.append(Item(channel=item.channel, title='Últimos Episodios', url=host + 'episodio/', action='list_all',
                         thumbnail=get_thumb('new episodes', auto=True), c_type='episodios'))
    
    itemlist.append(Item(channel=item.channel, title='Series', url=host + 'online/', action='list_all',
                         thumbnail=get_thumb('anime', auto=True), c_type='series'))
    
    itemlist.append(Item(channel=item.channel, title='Peliculas', url=host + 'pelicula/', action='list_all',
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Categorías',  action='sub_menu', url=host, 
                         thumbnail=get_thumb('categories', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Más Vistas', url=host + "tendencias/", action='list_all',
                         thumbnail=get_thumb('more watched', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Mejor Valoradas', url=host + "ratings/", action='list_all',
                         thumbnail=get_thumb('more voted', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Live Action', url=host + 'genero/live-action/', action='list_all',
                         thumbnail=get_thumb('anime', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Sin Censura', url=host + "genero/sin-censura/", action='list_all',
                         thumbnail=get_thumb('adults', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Latino', url=host + "genero/audio-latino/", action='list_all',
                         thumbnail=get_thumb('lat', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Castellano', url=host + "genero/anime-castellano/", action='list_all',
                         thumbnail=get_thumb('cast', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Blu-Ray/DVD', url=host + "genero/blu-ray-dvd/", action='list_all',
                         thumbnail=get_thumb('quality', auto=True)))

    itemlist.append(Item(channel=item.channel, title='Año', url=host + "release/", action='section',
                         thumbnail=get_thumb('year', auto=True), extra='Año'))

    return itemlist


def section(item):
    logger.info()

    return AlfaChannel.section(item, **kwargs)


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
            if item.c_type == 'search':
                elem_json['url'] = elem.a.get('href', '')
                elem_json['title'] = elem.img.get("alt", '').replace('VOSE', '')
                elem_json['thumbnail'] = elem.img.get('data-src', '') or elem.img.get('src', '')
                if elem.find("span", class_="year"): elem_json['year'] = elem.find("span", class_="year").get_text(strip=True)
                elem_json['mediatype'] = 'tvshow' if "online" in elem_json['url'] and not "pelicula" in elem_json['url'] else 'movie'

            else:
                if item.c_type == 'episodios':
                    sxe = elem.find("div", class_="poster").img.get("alt", '')
                    try:
                        season, episode = scrapertools.find_single_match(sxe, '(?i).*?(\d{1,2})(?:st|nd|er|th)\s*Season\s*Cap\s*(\d{1,3})')
                        elem_json['season'] = int(season)
                        elem_json['episode'] = int(episode)
                    except Exception:
                        elem_json['season'] = 1
                        elem_json['episode'] = int(scrapertools.find_single_match(sxe, '(?i).*?\s*Cap\s*(\d{1,3})') or 1)
                    elem_json['mediatype'] = 'episode'
                    elem_json['title'] = elem.find("div", class_="poster").img.get("alt", '').replace('VOSE', '')
                    elem_json['title'] = scrapertools.find_single_match(elem_json['title'],
                                                                        '(?i)(.*?)(?:\s*\d{1,2}(?:st|nd|er|th)\s*Season)?(?:\s*Cap\s*\d{1,3})')
                else:
                    elem_json['title'] = elem.find("div", class_="poster").img.get("alt", '').replace('VOSE', '')

                elem_json['url'] = elem.find("div", class_="poster").a.get('href', '')
                if not elem_json.get('mediatype'):
                    elem_json['mediatype'] = 'tvshow' if "online" in elem_json['url'] and not "pelicula" in elem_json['url'] else 'movie'
                elem_json['thumbnail'] = elem.find("div", class_="poster").img.get('data-src', '') \
                                         or elem.find("div", class_="poster").img.get('src', '')
                try:
                    elem_json['year'] = elem.find("div", class_="data").find("span", text=re.compile("\d{4}")).get_text(strip=True).split(",")[-1]
                except Exception:
                     elem_json['year'] = '-'

            elem_json['quality'] = '*'
            elem_json['language'] = '*VOSE'
            if elem.find("div", class_=["texto", "contenido"]): 
                elem_json['plot'] = elem.find("div", class_=["texto", "contenido"]).get_text(strip=True)
        
        except Exception:
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


def episodesxseason(item, **AHkwargs):
    logger.info()

    kwargs['matches_post_get_video_options'] = findvideos_matches
    soup = AHkwargs.get('soup', '')

    return AlfaChannel.episodes(item, data=soup, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()
    
    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem_season in matches_int:

        if elem_season.find("span", class_="se-t").get_text(strip=True) != str(item.contentSeason): continue
        epi_list = elem_season.find("ul", class_="episodios")

        if 'no hay episodios para' in str(epi_list):
            return matches

        for elem in epi_list.find_all("li"):
            elem_json = {}
            #logger.error(elem)

            try:
                info = elem.find("div", class_="episodiotitle")
                elem_json['url'] = info.a.get("href", "")
                elem_json['episode'] = int(elem.find("div", class_="numerando").get_text(strip=True).split(" - ")[1] or 1)
                elem_json['title'] = info.a.get_text(strip=True)
                elem_json['season'] = item.contentSeason
                elem_json['thumbnail'] = elem.img.get('data-src', '') or elem.img.get('src', '')

            except Exception:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

            if not elem_json.get('url', ''): 
                continue

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
    servers = {'fcom': 'fembed', 'dood': 'doodstream', 'hqq': '', 'youtube': '', 'saruch': '', 'supervideo': '', 'aparat': 'aparatcam'}

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['server'] = re.sub(r"\.\w{2,4}", "", elem.find("span", class_="server").get_text(strip=True).lower())
            elem_json['server'] = servers.get(elem_json['server'], elem_json['server'])
            if not elem_json['server']: continue
                
            elem_json['server'] = elem.find("span", class_="server").get_text(strip=True).lower()
            elem_json['language'] = '*%s' % re.sub(r'SERVER \d+ ', '', elem.find('span', class_='title').get_text(strip=True))
            elem_json['language'] = IDIOMAS.get(elem_json['language'].lower(), "VOSE")
            
            elem_json['url'] = ''
            elem_json['title'] = '%s'
            
            # Sistema movidy
            # NOTE: De vez en cuando cambian entre un sistema de la API REST
            # de WordPress, y uno de iframes, mantener el código comentado aquí
            if elem_json['server'] == 'saidochesto.top':

                if elem.find("li", id=re.compile(r"player-option-\d+")):
                    players = elem.find("li", id=re.compile(r"player-option-\d+"))
                    elem_json['url'] = players.find("iframe").get("src", "")

                else:
                    doo_url = "{}wp-json/dooplayer/v1/post/{}?type={}&source={}".format(
                               host, elem.get("data-post", ""), elem.get("data-type", ""), elem.get("data-nume", ""))

                    data = AlfaChannel.create_soup(doo_url, json=True, soup=False, **kwargs)

                    url = data.get("embed_url", "")

                new_soup = AlfaChannel.create_soup(url, **kwargs)
                
                new_soup = new_soup.find("div", class_="OptionsLangDisp")
                resultset = new_soup.find_all("li") if new_soup else []

                for elem in resultset:
                    try:
                        elem_json['url'] = scrapertools.find_single_match(elem.get("onclick", ""), r"\('([^']+)")
                        if "cloudemb.com" in elem_json['url'] or 'wolfstream' in elem_json['url']: continue

                        elem_json['server'] = re.sub(r"\.\w{2,4}", "", elem.find("span").get_text(strip=True).lower())
                        elem_json['server'] = servers.get(elem_json['server'], elem_json['server'])
                        if not elem_json['server']: continue
                        
                        elem_json['server'] = elem.find("span").get_text(strip=True)

                        elem_json['language'] = re.sub('\s+-.*', '', elem.find('p').get_text(strip=True))
                        elem_json['language'] = IDIOMAS.get(elem_json['language'].lower(), "VOSE")
                    
                    except Exception:
                        logger.error(elem)
                        logger.error(traceback.format_exc())
                        continue

                    if not elem_json.get('url'): continue

                    matches.append(elem_json.copy())

            else:
                 matches.append(elem_json.copy())

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

    return matches, langs


def play(item):
    logger.info()
    
    itemlist = []
    
    if 'embed.php' not in item.url:
        return [item]

    data = AlfaChannel.create_soup(item.url, soup=False, **kwargs)

    item.url = scrapertools.find_single_match(data, 'vp.setup\(\{.+?"file":"([^"]+).+?\);').replace("\\/", "/")
    item.server = ''

    itemlist.append(item.clone())
    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        texto = texto.replace(" ", "+")
        item.url = item.url + "?s=" + texto

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except Exception:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
