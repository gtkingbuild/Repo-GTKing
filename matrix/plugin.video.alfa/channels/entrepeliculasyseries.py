# -*- coding: utf-8 -*-
# -*- Channel EntrePeliculasySeries -*-
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
from core.httptools import channel_proxy_list
from channelselector import get_thumb
from platformcode import config, logger
from channels import filtertools, autoplay
from lib.AlfaChannelHelper import DictionaryAllChannel

IDIOMAS = {"latino": "LAT", "castellano": "CAST", "subtitulado": "VOSE"}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = ['DVDR', 'HDRip', 'VHSRip', 'HD', '2160p', '1080p', '720p', '4K', '3D', 'Screener', 'BluRay']
list_quality_tvshow = ['HDTV', 'HDTV-720p', 'WEB-DL 1080p', '4KWebRip']
list_servers = ['mega', 'fembed', 'vidtodo', 'gvideo']
forced_proxy_opt = 'ProxyCF'
host = 'https://entrepeliculasyseries.nz/'
assistant = config.get_setting('assistant_version', default='') and not channel_proxy_list(host)

canonical = {
             'channel': 'entrepeliculasyseries', 
             'host': config.get_setting("current_host", 'entrepeliculasyseries', default=''), 
             'host_alt': [host], 
             'host_black_list': ['https://entrepeliculasyseries.pro/', 'https://entrepeliculasyseries.nu/'],   
             'pattern_proxy': '(?i)<div\s*class="TpRwCont\s*Container">', 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF_stat': True if assistant else False, 'session_verify': True if assistant else False, 
             'CF_if_assistant': True if assistant else False, 'CF_if_NO_assistant': False,  
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = "/peli"
tv_path = '/serie'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['list-movie', 'MovieList']}]), 
                       ('find_all', [{'tag': ['li'], 'class': ['item', 'xxx TPostMv']}])]),
         'categories': {}, 
         'search': {}, 
         'get_language': dict([('find', [{'tag': ['span'], 'class': ["Lang"]}]), 
                               ('find_all', [{'tag': ['img']}])]),
         'get_language_rgx': '(?:flags\/|images\/)(\w+)\.(?:png|jpg|jpeg|webp)', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': {'find': [{'tag': ['a'], 'aria-label': ['Last Page'], '@ARG': 'href', '@TEXT': '\/(\d+)\/'}]}, 
         'year': dict([('find', [{'tag': ['h4']}]), 
                       ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]), 
         'season_episode': {'find': [{'tag': ['span'], 'class': ['Year'], '@TEXT': '(?i)(\d+x\d+)'}]}, 
         'seasons': dict([('find', [{'tag': ['select'], 'id': ['select-season']}]), 
                          ('find_all', [{'tag': ['option']}])]), 
         'season_num': [], 
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['article'], 'class': ['TPost C']}]}, 
         'episode_num': {}, 
         'episode_clean': [], 
         'plot': dict([('find', [{'tag': ['span'], 'class': ['lg margin-bottom']}]), 
                       ('get_text', [{'tag': '', '@STRIP': True}])]), 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['option-lang']}]},
         'title_clean': [['(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|ver\s*|\s*\(\d{4}\)', ''],
                         ['[\(|\[]\s*[\)|\]]', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu|calidad\s*', '']],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 18, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Peliculas', action='sub_menu', url=host + 'peliculas/', 
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Series',  action='sub_menu', url=host + 'series/', 
                         thumbnail=get_thumb('tvshows', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title='Anime',  action='list_all', url=host + 'anime/', 
                         thumbnail=get_thumb('anime', auto=True), c_type='series', extra='anime'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True), c_type='search'))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def sub_menu(item):
    logger.info()

    itemlist = list()

    itemlist.append(item.clone(title="Todas", action="list_all"))

    if item.c_type == "peliculas":
        itemlist.append(item.clone(title="Por Año", action="section", thumbnail=get_thumb('years.png'), url=host))

        itemlist.append(item.clone(title="Géneros", action="section", thumbnail=get_thumb('channels_anime.png')))

    elif item.c_type == "series":
        itemlist.append(item.clone(title="Últimas Series", action="list_all", url=host + 'series-recientes/', 
                                   thumbnail=get_thumb('popular.png')))

        itemlist.append(item.clone(title="Últimos Episodios", action="list_all", url=host + 'episodios/', 
                                   thumbnail=get_thumb('on_the_air.png'), c_type='episodios'))

        itemlist.append(item.clone(title="Episodios en Latino", action="list_all", url=host + 'capitulos-en-espanol-latino/', 
                                   thumbnail=get_thumb('channels_latino.png'), c_type='episodios'))

        itemlist.append(item.clone(title="Episodios en Castellano", action="list_all", url=host + 'capitulos-en-castellano/', 
                                   thumbnail=get_thumb('channels_spanish.png'), c_type='episodios'))

        itemlist.append(item.clone(title="Episodios Subtitulados", action="list_all", url=host + 'capitulos-en-sub-espanol/', 
                                   thumbnail=get_thumb('channels_vos.png'), c_type='episodios'))

        itemlist.append(item.clone(title='Productoras',  action='section', url=host + 'episodios/', 
                                   thumbnail=get_thumb('channels_anime.png')))

        itemlist.append(item.clone(title="Géneros", action="section", thumbnail=get_thumb('channels_anime.png')))

    return itemlist


def section(item):
    logger.info()

    findS = finds.copy()

    if 'Año' in item.title:
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['Wdgt movies_annee']}]), 
                                    ('find_all', [{'tag': ['li']}])])
        findS['controls'].update({'reverse': True})

    elif 'Productoras' in item.title:
        findS['categories'] = dict([('find', [{'tag': ['ul'], 'class': ['owl-carousel']}]), 
                                    ('find_all', [{'tag': ['li'], 'class': ['item']}])])

    elif 'Géneros' in item.title:
        findS['categories'] = {'find_all': [{'tag': ['li'], 'class': ['AAIco-video_library']}]}

    return AlfaChannel.section(item, matches_post=section_matches, finds=findS, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    if 'Año' in item.title:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)

            elem_json['url'] = elem.a["href"]
            elem_json['title'] = elem.a.text

            matches.append(elem_json.copy())

    elif 'Productoras' in item.title:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)

            elem_json['url'] = elem.a.get('href', '')
            elem_json['title'] = elem.find('div', class_="category-name").get_text(strip=True)
            elem_json['title'] += ' (%s)' % elem.find('div', class_="category-description").get_text(strip=True)
            elem_json['thumbnail'] = elem.find('img', class_="ico-category").get('src')
            if AlfaChannel.response_proxy: elem_json['thumbnail'] = get_thumb('channels_anime.png')

            matches.append(elem_json.copy())
    
    elif 'Géneros' in item.title:
        for elem in matches_int:
            elem_json = {}
            #logger.error(elem)

            elem_json['url'] = elem.a.get('href', '')
            if '/%s' % item.c_type not in elem_json['url']:
                if item.c_type == 'peliculas' and '/documentales' not in elem_json['url']:
                    continue
                elif item.c_type == 'series':
                    continue
            elem_json['title'] = elem.a.get_text(strip=True)

            matches.append(elem_json.copy())

    return matches or matches_int


def list_all(item):
    logger.info()

    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    sxe = ''

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            if item.c_type == 'episodios':
                try:
                    sxe = AlfaChannel.parse_finds_dict(elem, findS.get('season_episode', {}), c_type=item.c_type)
                    if not sxe: continue
                    elem_json['season'], elem_json['episode'] = sxe.split('x')
                    elem_json['season'] = int(elem_json['season'] or 1)
                    elem_json['episode'] = int(elem_json['episode'] or 1)
                except:
                    elem_json['season'] = 1
                    elem_json['episode'] = 1
                elem_json['year'] = '-'
                AlfaChannel.get_language_and_set_filter(elem, elem_json)
                if elem_json['language']:
                    elem_json['language'] = '*%s' % elem_json['language']
                else:
                    elem_json['language'] = '*lat' if 'Latino' in item.title else '*cast' if 'Castellano' in item.title else '*sub'

            elem_json['url'] = elem.a.get('href', '').replace('#', '') or elem.find('a', class_="link-title").get('href', '')
            elem_json['title'] = elem.find('h2').get_text(strip=True).strip()
            elem_json['thumbnail'] = elem.img.get('data-src', '') or elem.find('figure', class_='Objf').get('data-src', '')
            elem_json['year'] = elem_json.get('year', AlfaChannel.parse_finds_dict(elem, findS.get('year', {}), year=True, c_type=item.c_type))
            elem_json['plot'] = AlfaChannel.parse_finds_dict(elem, findS.get('plot', {}), c_type=item.c_type)

            if not elem_json['url']: continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

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
            sxe = AlfaChannel.parse_finds_dict(elem, findS.get('season_episode', {}), c_type=item.c_type)
            if not sxe: continue
            elem_json['season'], elem_json['episode'] = sxe.split('x')
            elem_json['season'] = int(elem_json['season'] or 1)
            elem_json['episode'] = int(elem_json['episode'] or 1)
        except:
            elem_json['season'] = 1
            elem_json['episode'] = 1
            logger.error(elem)
            logger.error(traceback.format_exc())
        if item.contentSeason != elem_json.get('season', 1): continue
        elem_json['year'] = '-'

        elem_json['url'] = elem.a.get('href', '')
        elem_json['title'] = elem.find('h2').get_text(strip=True).strip()
        elem_json['thumbnail'] = elem.img.get('data-src', '')

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

    servers = {'drive': 'gvideo', 'fembed': 'fembed', "player": "oprem", "openplay": "oprem", "embed": "mystream"}

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:
            elem_json['language'] = '*%s' % elem.find('h3', class_="select-idioma").get_text('|', strip=True).split('|')[0]
            if "descargar" in str(elem_json['language']).lower(): continue
            elem_json['quality'] = '*%s' % elem.find('h3', class_="select-idioma").get_text('|', strip=True).split('|')[1]
            elem_json['title'] = '%s'
            
            for link in elem.find_all('li', class_='option'):
                try:
                    elem_json['server'] = link.get_text(strip=True).lower()
                    elem_json['url'] = link.get('data-link', '')

                    if not elem_json['url']: continue

                    if elem_json['server'].lower() in ["waaw", "jetload"]: continue
                    if elem_json['server'].lower() in servers:
                       elem_json['server'] = servers[elem_json['server'].lower()]

                    matches.append(elem_json.copy())
                except:
                    logger.error(traceback.format_exc())
                    continue
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

    return matches, langs


def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)
    

def play(item):
    
    itemlist = list()
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 'timeout': 5, 
              'canonical': {}, 'soup': False}

    id = scrapertools.find_single_match(item.url, "h=([^$]+)")
    headers = item.headers or {"Referer": item.url}

    post = None
    base_url = item.url
    url = ''
    
    for x in range(2):
        resp = AlfaChannel.create_soup(base_url, post=post, headers=headers, follow_redirects=False, 
                                       forced_proxy_opt=forced_proxy_opt, **kwargs)
        url = AlfaChannel.get_cookie(url, 'nofernu')
        if url:
            url = AlfaChannel.do_unquote(url)
            break
        
        post = {"h": id}
        base_url = "%sr.php" % host
        if resp.code in AlfaChannel.REDIRECTION_CODES:
            url = resp.headers.get("location", "")
            break
    
    if url and not url.startswith("http"):
        url = "https:" + url
    item.server = ""
    itemlist.append(item.clone(url=url))

    itemlist = servertools.get_servers_itemlist(itemlist)
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        texto = texto.replace(" ", "+")
        item.url = host + '?s=' + texto

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = host + 'peliculas/'
        elif categoria == 'infantiles':
            item.url = host + 'peliculas-de-animacion/'
        elif categoria == 'terror':
            item.url = host + 'peliculas-de-terror/'
        itemlist = list_all(item)
        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def play_netu(item):

    domain = AlfaChannel.obtain_domain(item.url, scheme=True)
    
    itemlist = list()
    kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 0, 'ignore_response_code': True, 'timeout': 5, 
              'CF': True, 'canonical': {}, 'soup': False}
    
    headers = {"Referer": item.url}
    url = '%s?=&best=t' % item.url
    
    resp = AlfaChannel.create_soup(url, headers=headers, follow_redirects=False, 
                                   forced_proxy_opt=forced_proxy_opt, **kwargs)
    if resp.code in AlfaChannel.REDIRECTION_CODES:
        url = resp.headers.get("location", "")
    else:
        return []
    
    headers = {"Referer": url}
    domain_e = AlfaChannel.obtain_domain(url, scheme=True)
    url = '%s/f/%s?http_referer=%s' % (domain_e, scrapertools.find_single_match(url, "\?v=([^$]+)"), AlfaChannel.do_quote(domain+'/'))
    resp = AlfaChannel.create_soup(url, headers=headers, follow_redirects=False, 
                                   forced_proxy_opt=forced_proxy_opt, **kwargs)

    #url = scrapertools.find_single_match(resp.data, "self\.location\.replace\('([^']+)'").replace('#', '%23')
    url = scrapertools.find_single_match(resp.data, "self\.location\.replace\('([^']+)'").split('&')[0]
    url = AlfaChannel.urljoin(domain_e, url)
    resp = AlfaChannel.create_soup(url, headers=headers, follow_redirects=False, 
                                   forced_proxy_opt=forced_proxy_opt, **kwargs)
                                   
    url = scrapertools.find_single_match(resp.data, "self\.location\.replace\('([^']+)'")
    url = AlfaChannel.urljoin(domain_e, url)
    resp = AlfaChannel.create_soup(url, headers=headers, follow_redirects=False, 
                                   forced_proxy_opt=forced_proxy_opt, **kwargs)

    logger.error(resp.data)
    
    item.server = ""
    itemlist.append(item.clone(url=url))

    itemlist = servertools.get_servers_itemlist(itemlist)
    
    return itemlist
